from __future__ import annotations

import base64
import json
import stat
import typing as t
from datetime import datetime, timedelta
from datetime import timezone as tz

import pytest

from meltano.core.cloud.credentials import Credentials, CredentialsStore

if t.TYPE_CHECKING:
    from pathlib import Path


def make_id_token(claims: dict[str, t.Any]) -> str:
    """Build an unsigned JWT with the given claims."""
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
    return f"header.{payload}.signature"


class TestCredentials:
    def test_from_token_response(self) -> None:
        credentials = Credentials.from_token_response(
            {
                "access_token": "at",
                "refresh_token": "rt",
                "id_token": "it",
                "token_type": "Bearer",
                "expires_in": 86400,
                "scope": "openid",
            },
        )
        assert credentials.access_token == "at"
        assert credentials.refresh_token == "rt"
        assert credentials.id_token == "it"
        assert credentials.scope == "openid"
        assert credentials.expires_at is not None
        assert not credentials.is_expired

    def test_from_token_response_keeps_previous_refresh_token(self) -> None:
        credentials = Credentials.from_token_response(
            {"access_token": "at", "expires_in": 60},
            refresh_token="previous",
        )
        assert credentials.refresh_token == "previous"

    def test_round_trip(self) -> None:
        expires_at = datetime.now(tz=tz.utc) + timedelta(hours=1)
        credentials = Credentials(
            access_token="at",
            refresh_token="rt",
            id_token="it",
            expires_at=expires_at,
            scope="openid",
        )
        assert Credentials.from_dict(credentials.to_dict()) == credentials

    def test_to_dict_omits_empty_values(self) -> None:
        assert Credentials(access_token="at").to_dict() == {
            "access_token": "at",
            "token_type": "Bearer",
        }

    @pytest.mark.parametrize(
        ("delta", "expired"),
        ((timedelta(hours=1), False), (timedelta(seconds=-1), True)),
    )
    def test_is_expired(self, delta: timedelta, expired: bool) -> None:  # noqa: FBT001
        credentials = Credentials(
            access_token="at",
            expires_at=datetime.now(tz=tz.utc) + delta,
        )
        assert credentials.is_expired is expired

    def test_is_expired_within_leeway(self) -> None:
        # A token that expires in 30 seconds is treated as expired, so that it
        # is not rejected between being read and being used.
        credentials = Credentials(
            access_token="at",
            expires_at=datetime.now(tz=tz.utc) + timedelta(seconds=30),
        )
        assert credentials.is_expired

    def test_never_expires_without_expiry(self) -> None:
        assert not Credentials(access_token="at").is_expired

    def test_auth_header(self) -> None:
        credentials = Credentials(access_token="at", token_type="Bearer")
        assert credentials.auth_header == {"Authorization": "Bearer at"}

    def test_claims(self) -> None:
        credentials = Credentials(
            access_token="at",
            id_token=make_id_token({"email": "user@example.com"}),
        )
        assert credentials.claims["email"] == "user@example.com"

    @pytest.mark.parametrize("id_token", ("", "not-a-jwt", "a.!!!.c"))
    def test_claims_of_invalid_token(self, id_token: str) -> None:
        assert Credentials(access_token="at", id_token=id_token).claims == {}

    def test_with_token_response_keeps_id_token(self) -> None:
        credentials = Credentials(access_token="at", refresh_token="rt", id_token="it")
        # Auth0 omits the ID token, and the refresh token unless rotation is
        # enabled, from refresh responses.
        refreshed = credentials.with_token_response(
            {"access_token": "new-at", "expires_in": 60},
        )
        assert refreshed.access_token == "new-at"
        assert refreshed.refresh_token == "rt"
        assert refreshed.id_token == "it"

    def test_with_token_response_accepts_rotated_tokens(self) -> None:
        credentials = Credentials(access_token="at", refresh_token="rt", id_token="it")
        refreshed = credentials.with_token_response(
            {"access_token": "new-at", "refresh_token": "new-rt", "id_token": "new-it"},
        )
        assert refreshed.refresh_token == "new-rt"
        assert refreshed.id_token == "new-it"


class TestCredentialsStore:
    @pytest.fixture
    def store(self, tmp_path: Path) -> CredentialsStore:
        return CredentialsStore(tmp_path / "cloud" / "credentials.json")

    def test_get_when_missing(self, store: CredentialsStore) -> None:
        assert store.get() is None

    def test_set_and_get(self, store: CredentialsStore) -> None:
        credentials = Credentials(access_token="at", refresh_token="rt")
        store.set(credentials)
        assert CredentialsStore(store.path).get() == credentials

    def test_set_is_user_readable_only(self, store: CredentialsStore) -> None:
        store.set(Credentials(access_token="at"))
        assert stat.S_IMODE(store.path.stat().st_mode) == 0o600

    def test_set_leaves_no_temporary_file(self, store: CredentialsStore) -> None:
        store.set(Credentials(access_token="at"))
        assert [path.name for path in store.path.parent.iterdir()] == [store.path.name]

    def test_set_replaces_existing_credentials(self, store: CredentialsStore) -> None:
        store.set(Credentials(access_token="first"))
        store.set(Credentials(access_token="second"))
        assert CredentialsStore(store.path).get().access_token == "second"

    def test_clear(self, store: CredentialsStore) -> None:
        store.set(Credentials(access_token="at"))
        assert store.clear() is True
        assert not store.path.exists()
        assert store.get() is None

    def test_clear_when_missing(self, store: CredentialsStore) -> None:
        assert store.clear() is False

    @pytest.mark.parametrize("content", ("{not json", "{}", '{"access_token": null}'))
    def test_get_malformed(self, store: CredentialsStore, content: str) -> None:
        store.path.parent.mkdir(parents=True)
        store.path.write_text(content)
        assert store.get() is None
