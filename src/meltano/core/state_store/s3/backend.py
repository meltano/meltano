"""StateStoreManager for S3 cloud storage backend."""

from __future__ import annotations

import re
import sys
import typing as t
from contextlib import contextmanager, suppress
from datetime import datetime, timedelta, timezone
from functools import cached_property
from time import sleep
from urllib.parse import urlparse

import boto3
import structlog
from botocore.exceptions import ClientError

from meltano.core.state_store.base import (
    MeltanoState,
    MissingStateBackendSettingsError,
    StateStoreManager,
)

if sys.version_info >= (3, 12):
    from typing import override  # noqa: ICN003
else:
    from typing_extensions import override

if t.TYPE_CHECKING:
    from collections.abc import Generator

    from mypy_boto3_s3 import S3Client

logger = structlog.stdlib.get_logger(__name__)


class S3StateStoreManager(StateStoreManager):
    """State backend for S3 using pure boto3 implementation."""

    label: str = "AWS S3"

    @override
    def __init__(
        self,
        uri: str,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        bucket: str | None = None,
        prefix: str | None = None,
        endpoint_url: str | None = None,
        lock_timeout_seconds: int = 300,
        **kwargs: t.Any,
    ):
        """Initialize the S3StateStoreManager.

        Args:
            uri: the URI for the state backend (s3://bucket/prefix)
            aws_access_key_id: AWS access key ID used to authenticate
            aws_secret_access_key: AWS secret access key used to authenticate
            bucket: the bucket to store state in
            prefix: the prefix to store state at
            endpoint_url: the endpoint url for S3
            lock_timeout_seconds: how many seconds a lock should be considered active
            kwargs: additional keyword args to pass to parent
        """
        super().__init__(**kwargs)
        self.uri = uri
        self.lock_timeout_seconds = lock_timeout_seconds
        self.parsed = urlparse(self.uri)

        # Extract credentials from URI or use provided values
        self.aws_access_key_id = aws_access_key_id or self.parsed.username
        self.aws_secret_access_key = aws_secret_access_key or self.parsed.password

        # Extract bucket and prefix from URI or use provided values
        self.bucket: str = bucket or self.parsed.hostname  # type: ignore[assignment]
        # Keep the raw prefix (with leading slash) for list_objects_v2 compatibility
        # But strip slashes when building keys via state_dir
        raw_prefix = prefix or self.parsed.path or ""
        self._raw_prefix = raw_prefix.rstrip("/") if raw_prefix else ""
        self.endpoint_url = endpoint_url

        if not self.bucket:
            msg = "S3 bucket name is required. Provide it via URI or bucket parameter."
            raise MissingStateBackendSettingsError(msg)

    @cached_property
    def client(self) -> S3Client:
        """Get an authenticated boto3 S3 Client.

        Returns:
            A boto3 S3 Client.

        Raises:
            InvalidStateBackendConfigurationException: when configured AWS
                settings are invalid.
        """
        if self.aws_secret_access_key and self.aws_access_key_id:
            session = boto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
            )
            return session.client("s3", endpoint_url=self.endpoint_url)
        if self.aws_secret_access_key:
            msg = "AWS secret access key configured, but not AWS access key ID."
            raise MissingStateBackendSettingsError(msg)
        if self.aws_access_key_id:
            msg = "AWS access key ID configured, but no AWS secret access key."
            raise MissingStateBackendSettingsError(msg)
        session = boto3.Session()
        return session.client("s3", endpoint_url=self.endpoint_url)

    @property
    def prefix(self) -> str:
        """Get the raw prefix (with leading slash if present).

        Returns:
            The raw prefix for use in list_objects_v2
        """
        return self._raw_prefix

    @property
    def state_dir(self) -> str:
        """Get the prefix that state should be stored at.

        Returns:
            The relevant prefix (with leading and trailing slashes stripped)
        """
        return self._raw_prefix.lstrip("/").rstrip("/")

    def _get_s3_key(self, state_id: str, filename: str | None = None) -> str:
        """Build the S3 key for a given state_id and optional filename.

        Args:
            state_id: the state_id
            filename: optional filename (e.g., "state.json", "lock")

        Returns:
            The S3 key path (without leading slash)
        """
        # Use state_dir (without leading slash) to build keys
        parts = [self.state_dir, state_id] if self.state_dir else [state_id]
        if filename:
            parts.append(filename)
        return "/".join(parts)

    @staticmethod
    def is_file_not_found_error(err: Exception) -> bool:
        """Check if err is equivalent to file not being found.

        Args:
            err: the err to check

        Returns:
            True if error represents file not being found, else False
        """
        return (
            isinstance(err, ClientError)
            and err.response["Error"]["Code"] == "NoSuchKey"
        )

    def delete_file(self, file_path: str) -> None:
        """Delete the file/blob at the given path.

        Args:
            file_path: the path to delete.
        """
        self.client.delete_objects(
            Bucket=self.bucket,
            Delete={"Objects": [{"Key": file_path}]},
        )

    def get(self, state_id: str) -> MeltanoState | None:
        """Get current state for the given state_id.

        Args:
            state_id: the state_id to get state for.

        Returns:
            Current state, if any exists, else None
        """
        logger.info("Reading state from %s", self.label)
        state_key = self._get_s3_key(state_id, "state.json")

        try:
            response = self.client.get_object(Bucket=self.bucket, Key=state_key)
            state_json = response["Body"].read().decode("utf-8")
            return MeltanoState.from_json(state_id, state_json)
        except Exception as e:
            # Check if it's a GLACIER storage class error
            if "InvalidObjectState" in str(e):
                msg = f"unable to access {state_key}"
                raise OSError(msg) from e
            if self.is_file_not_found_error(e):
                logger.info("No state found for %s.", state_id)
                return None
            raise

    @override
    def set(self, state: MeltanoState) -> None:
        """Set state for the given state_id.

        Args:
            state: the state to set
        """
        logger.info("Writing state to %s", self.label)
        state_key = self._get_s3_key(state.state_id, "state.json")

        self.client.put_object(
            Bucket=self.bucket,
            Key=state_key,
            Body=state.json().encode("utf-8"),
            ContentType="application/json",
        )

    @override
    def delete(self, state_id: str) -> None:
        """Clear state for the given state_id.

        Args:
            state_id: the state_id to clear state for.
        """
        state_key = self._get_s3_key(state_id, "state.json")
        self.client.delete_object(Bucket=self.bucket, Key=state_key)

    @override
    def get_state_ids(self, pattern: str | None = None) -> list[str]:
        """Get list of state_ids stored in the backend.

        Args:
            pattern: glob-style pattern to filter state_ids by

        Returns:
            List of state_ids
        """
        pattern_re = re.compile(pattern.replace("*", ".*")) if pattern else None
        state_ids = set()

        # List all objects with the prefix (no trailing slash for list operation)
        paginator = self.client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=self.bucket, Prefix=self.prefix)

        for page in pages:
            for obj in page.get("Contents", []):
                key = obj["Key"]
                # Remove prefix from key if present (keys don't have leading slash)
                if self.state_dir and key.startswith(self.state_dir):
                    remaining = key[len(self.state_dir) :].lstrip("/")
                else:
                    remaining = key

                # Extract state_id from path like "state_id/state.json"
                parts = remaining.split("/")
                if len(parts) >= 2 and parts[-1] == "state.json":
                    state_id = parts[-2]
                    if pattern_re is None or pattern_re.match(state_id):
                        state_ids.add(state_id)

        return list(state_ids)

    def _is_locked(self, state_id: str) -> bool:
        """Check if the given state_id is currently locked.

        Args:
            state_id: the state_id to check

        Returns:
            True if locked, else False
        """
        lock_key = self._get_s3_key(state_id, "lock")

        try:
            response = self.client.get_object(Bucket=self.bucket, Key=lock_key)
            locked_at_str = response["Body"].read().decode("utf-8")
            locked_at = datetime.fromtimestamp(
                float(locked_at_str),
                tz=timezone.utc,
            )

            # Check if lock has expired
            if locked_at < (
                datetime.now(timezone.utc)
                - timedelta(seconds=self.lock_timeout_seconds)
            ):
                # Lock has expired, delete it
                self.client.delete_object(Bucket=self.bucket, Key=lock_key)
                return False

            return True
        except self.client.exceptions.NoSuchKey:
            return False
        except Exception as e:
            if self.is_file_not_found_error(e):
                return False
            raise

    @override
    @contextmanager
    def acquire_lock(
        self,
        state_id: str,
        *,
        retry_seconds: int,
    ) -> Generator[None, None, None]:
        """Acquire a naive lock for the given state_id.

        Args:
            state_id: the state_id to lock
            retry_seconds: the number of seconds to wait before retrying

        Yields:
            None
        """
        lock_key = self._get_s3_key(state_id, "lock")

        try:
            # Wait for any existing lock to be released
            while self._is_locked(state_id):
                sleep(retry_seconds)

            # Create the lock
            timestamp = str(datetime.now(timezone.utc).timestamp())
            self.client.put_object(
                Bucket=self.bucket,
                Key=lock_key,
                Body=timestamp.encode("utf-8"),
                ContentType="application/json",
            )

            yield
        finally:
            # Release the lock
            with suppress(Exception):
                self.client.delete_object(Bucket=self.bucket, Key=lock_key)
