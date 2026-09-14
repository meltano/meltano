"""Storage for Meltano Cloud credentials."""

from __future__ import annotations

import base64
import binascii
import json
import os
import typing as t
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from datetime import timezone as tz

import structlog

if t.TYPE_CHECKING:
    from pathlib import Path

logger = structlog.stdlib.get_logger(__name__)

# Treat tokens that are about to expire as expired, so that a token is not
# rejected by the API between being read and being used.
EXPIRY_LEEWAY = timedelta(seconds=60)

# Only the current user may read or write the credentials file.
CREDENTIALS_FILE_MODE = 0o600
CREDENTIALS_DIR_MODE = 0o700


def _decode_jwt_claims(token: str) -> dict[str, t.Any]:
    """Decode the claims of a JWT without verifying its signature.

    The ID token is received directly from Auth0 over TLS, and the claims are
    only used to display information about the logged in user, so no signature
    verification is performed here. Never use these claims to make an
    authorization decision.

    Args:
        token: The JWT to decode.

    Returns:
        The decoded claims, or an empty dict if they could not be decoded.
    """
    try:
        payload = token.split(".")[1]
        padded = payload + "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(padded))
    except (IndexError, ValueError, binascii.Error, UnicodeDecodeError):
        logger.debug("Unable to decode ID token claims")
        return {}


@dataclass(frozen=True, slots=True)
class Credentials:
    """A Meltano Cloud session."""

    access_token: str
    token_type: str = "Bearer"  # noqa: S105
    refresh_token: str | None = None
    id_token: str | None = None
    expires_at: datetime | None = None
    scope: str | None = None

    @classmethod
    def from_token_response(
        cls,
        data: dict[str, t.Any],
        *,
        refresh_token: str | None = None,
    ) -> Credentials:
        """Create credentials from an Auth0 token endpoint response.

        Args:
            data: The decoded token endpoint response.
            refresh_token: The refresh token to fall back to. Auth0 omits the
                refresh token from refresh responses unless rotation is
                enabled, in which case the previous one remains valid.

        Returns:
            The credentials.
        """
        expires_at = None
        if expires_in := data.get("expires_in"):
            expires_at = datetime.now(tz=tz.utc) + timedelta(seconds=int(expires_in))

        return cls(
            access_token=data["access_token"],
            token_type=data.get("token_type", "Bearer"),
            refresh_token=data.get("refresh_token") or refresh_token,
            id_token=data.get("id_token"),
            expires_at=expires_at,
            scope=data.get("scope"),
        )

    @classmethod
    def from_dict(cls, data: dict[str, t.Any]) -> Credentials:
        """Create credentials from their serialized form.

        Args:
            data: The serialized credentials.

        Returns:
            The credentials.

        Raises:
            ValueError: If the serialized credentials have no access token.
        """
        if not data.get("access_token"):
            msg = "No access token is present"
            raise ValueError(msg)

        expires_at = None
        if raw_expires_at := data.get("expires_at"):
            expires_at = datetime.fromisoformat(raw_expires_at)
            if expires_at.tzinfo is None:  # pragma: no cover
                expires_at = expires_at.replace(tzinfo=tz.utc)

        return cls(
            access_token=data["access_token"],
            token_type=data.get("token_type", "Bearer"),
            refresh_token=data.get("refresh_token"),
            id_token=data.get("id_token"),
            expires_at=expires_at,
            scope=data.get("scope"),
        )

    def to_dict(self) -> dict[str, t.Any]:
        """Serialize the credentials.

        Returns:
            The serialized credentials.
        """
        data: dict[str, t.Any] = {
            "access_token": self.access_token,
            "token_type": self.token_type,
        }
        if self.refresh_token:
            data["refresh_token"] = self.refresh_token
        if self.id_token:
            data["id_token"] = self.id_token
        if self.expires_at:
            data["expires_at"] = self.expires_at.isoformat()
        if self.scope:
            data["scope"] = self.scope
        return data

    @property
    def is_expired(self) -> bool:
        """Whether the access token has expired, or is about to."""
        if self.expires_at is None:
            return False
        return datetime.now(tz=tz.utc) >= (self.expires_at - EXPIRY_LEEWAY)

    @property
    def claims(self) -> dict[str, t.Any]:
        """The unverified claims of the ID token."""
        return _decode_jwt_claims(self.id_token) if self.id_token else {}

    @property
    def auth_header(self) -> dict[str, str]:
        """The `Authorization` header to use for Meltano Cloud API calls."""
        return {"Authorization": f"{self.token_type} {self.access_token}"}

    def with_token_response(self, data: dict[str, t.Any]) -> Credentials:
        """Create updated credentials from a token endpoint response.

        Args:
            data: The decoded token endpoint response.

        Returns:
            The updated credentials.
        """
        refreshed = Credentials.from_token_response(
            data,
            refresh_token=self.refresh_token,
        )
        # Auth0 only returns an ID token when 'openid' was requested, which is
        # not the case for a refresh, so keep the one we already have.
        return replace(refreshed, id_token=refreshed.id_token or self.id_token)


@dataclass(slots=True)
class CredentialsStore:
    """Reads and writes Meltano Cloud credentials on the local filesystem."""

    path: Path
    _cache: Credentials | None = field(default=None, init=False, repr=False)

    def get(self) -> Credentials | None:
        """Read the stored credentials.

        Returns:
            The stored credentials, or `None` if no valid credentials are
            stored.
        """
        if self._cache is not None:
            return self._cache

        try:
            data = json.loads(self.path.read_text())
        except FileNotFoundError:
            return None
        except (OSError, ValueError) as err:
            logger.warning(
                "Unable to read Meltano Cloud credentials",
                path=str(self.path),
                error=str(err),
            )
            return None

        try:
            self._cache = Credentials.from_dict(data)
        except (KeyError, TypeError, ValueError) as err:
            logger.warning(
                "Stored Meltano Cloud credentials are malformed",
                path=str(self.path),
                error=str(err),
            )
            return None

        return self._cache

    def set(self, credentials: Credentials) -> None:
        """Write credentials to the store, replacing any existing credentials.

        The credentials file is only readable and writable by the current user.

        Args:
            credentials: The credentials to store.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=CREDENTIALS_DIR_MODE)

        # Write to a temporary file in the same directory and move it into
        # place, so that a partial write can never clobber a valid session.
        tmp_path = self.path.with_name(f"{self.path.name}.tmp")
        fd = os.open(
            tmp_path,
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
            CREDENTIALS_FILE_MODE,
        )
        try:
            with open(fd, "w", closefd=True) as tmp_file:  # noqa: PTH123
                json.dump(credentials.to_dict(), tmp_file, indent=2)
                tmp_file.write("\n")
            tmp_path.replace(self.path)
        except BaseException:
            tmp_path.unlink(missing_ok=True)
            raise

        self._cache = credentials

    def clear(self) -> bool:
        """Delete any stored credentials.

        Returns:
            Whether credentials were deleted.
        """
        self._cache = None
        try:
            self.path.unlink()
        except FileNotFoundError:
            return False
        except OSError as err:
            logger.warning(
                "Unable to delete Meltano Cloud credentials",
                path=str(self.path),
                error=str(err),
            )
            return False
        return True
