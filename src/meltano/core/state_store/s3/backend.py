"""StateStoreManager for S3 cloud storage backend."""

from __future__ import annotations

import sys
import typing as t
from functools import cached_property

import boto3
from botocore.config import Config

from meltano.core.state_store.filesystem import (
    CloudStateStoreManager,
    InvalidStateBackendConfigurationException,
)

if sys.version_info >= (3, 12):
    from typing import override  # noqa: ICN003
else:
    from typing_extensions import override

if t.TYPE_CHECKING:
    from collections.abc import Iterable

    from mypy_boto3_s3 import S3Client

    from meltano.core.state_store.base import MeltanoState

    if sys.version_info >= (3, 13):
        from collections.abc import Generator
    else:
        from typing_extensions import Generator


class S3StateStoreManager(CloudStateStoreManager):
    """State backend for S3."""

    label: str = "AWS S3"

    def __init__(
        self,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        bucket: str | None = None,
        prefix: str | None = None,
        endpoint_url: str | None = None,
        **kwargs: t.Any,
    ):
        """Initialize the BaseFilesystemStateStoreManager.

        Args:
            aws_access_key_id: AWS access key ID used to authenticate
            aws_secret_access_key: AWS secret access key used to authenticate
            bucket: the bucket to store state in
            prefix: the prefix to store state at
            endpoint_url: the endpoint url for S3
            kwargs: additional keyword args to pass to parent
        """
        super().__init__(**kwargs)
        self.aws_access_key_id = aws_access_key_id or self.parsed.username
        self.aws_secret_access_key = aws_secret_access_key or self.parsed.password

        # TODO: Make this type-safe. Maybe use https://github.com/fsspec/universal_pathlib?
        self.bucket: str = bucket or self.parsed.hostname  # type: ignore[assignment]  # ty:ignore[invalid-assignment]
        self.prefix = prefix or self.parsed.path
        self.endpoint_url = endpoint_url

    @staticmethod
    @override
    def is_file_not_found_error(err: Exception) -> bool:
        """Check if err is equivalent to file not being found.

        Args:
            err: the err to check

        Returns:
            True if error represents file not being found, else False
        """
        return (isinstance(err, OSError) and "NoSuchKey" in err.args[0]) or (
            isinstance(err, KeyError) and "ActualObjectSize" in err.args[0]
        )

    @property
    @override
    def extra_transport_params(self) -> dict[str, t.Any]:
        """Extra transport params for ``smart_open.open``.

        Returns:
            A dictionary of extra transport params.
        """
        return {
            "client_kwargs": {
                "S3.Client.create_multipart_upload": {
                    "ContentType": "application/json",
                },
            },
        }

    @cached_property
    @override
    def client(self) -> S3Client:
        """An authenticated boto3.Client.

        Raises:
            InvalidStateBackendConfigurationException: when configured AWS
                settings are invalid.
        """
        config = Config(user_agent_extra="meltano")

        if self.aws_secret_access_key and self.aws_access_key_id:
            session = boto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
            )
            return session.client("s3", endpoint_url=self.endpoint_url, config=config)
        if self.aws_secret_access_key:
            raise InvalidStateBackendConfigurationException(  # noqa: TRY003
                "AWS secret access key configured, but not AWS access key ID.",  # noqa: EM101
            )
        if self.aws_access_key_id:
            raise InvalidStateBackendConfigurationException(  # noqa: TRY003
                "AWS access key ID configured, but no AWS secret access key.",  # noqa: EM101
            )
        session = boto3.Session()
        return session.client("s3", config=config)

    @override
    def set_all(self, states: Iterable[MeltanoState]) -> int:
        """Write multiple states via direct ``PutObject`` calls.

        Bypasses ``smart_open``'s multipart-upload setup, which is wasteful
        for the small JSON payloads that state files typically contain.

        Args:
            states: iterable of MeltanoState objects to persist
        """
        count = 0
        for state in states:
            self.client.put_object(
                Bucket=self.bucket,
                Key=self.get_state_path(state.state_id),
                Body=state.json().encode(),
                ContentType="application/json",
            )
            count += 1
        return count

    @override
    def delete_file(self, file_path: str) -> None:
        """Delete the file/blob at the given path.

        Args:
            file_path: the path to delete.
        """
        self.client.delete_objects(
            Bucket=self.bucket,
            Delete={"Objects": [{"Key": file_path}]},
        )

    @override
    def list_all_files(self, *, with_prefix: bool = True) -> Generator[str]:
        """List all files in the backend.

        Args:
            with_prefix: Whether to include the prefix in the lookup.

        Yields:
            The path to each file in the backend.
        """
        kwargs: dict[str, t.Any] = {"Bucket": self.bucket}
        if with_prefix:
            kwargs["Prefix"] = self.state_dir

        paginator = self.client.get_paginator("list_objects_v2")
        for page in paginator.paginate(**kwargs):
            for state_obj in page.get("Contents", []):
                yield state_obj["Key"]

    @override
    def copy_file(self, src: str, dst: str) -> None:
        """Copy a file from one path to another.

        Args:
            src: the source path
            dst: the destination path
        """
        self.client.copy_object(
            Bucket=self.bucket,
            CopySource={"Bucket": self.bucket, "Key": src},
            Key=dst,
        )
