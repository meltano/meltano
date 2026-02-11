"""StateStoreManager for S3 cloud storage backend."""

from __future__ import annotations

import typing as t
from functools import cached_property

import boto3

from meltano.core.state_store.filesystem import (
    CloudStateStoreManager,
    InvalidStateBackendConfigurationException,
)

if t.TYPE_CHECKING:
    from collections.abc import Generator

    from mypy_boto3_s3 import S3Client


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
        self.bucket: str = bucket or self.parsed.hostname  # type: ignore[assignment]
        self.prefix = prefix or self.parsed.path
        self.endpoint_url = endpoint_url

    @staticmethod
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
    def client(self) -> S3Client:
        """Get an authenticated boto3.Client.

        Returns:
            A boto3.Client.

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
            raise InvalidStateBackendConfigurationException(  # noqa: TRY003
                "AWS secret access key configured, but not AWS access key ID.",  # noqa: EM101
            )
        if self.aws_access_key_id:
            raise InvalidStateBackendConfigurationException(  # noqa: TRY003
                "AWS access key ID configured, but no AWS secret access key.",  # noqa: EM101
            )
        session = boto3.Session()
        return session.client("s3")

    def delete_file(self, file_path: str) -> None:
        """Delete the file/blob at the given path.

        Args:
            file_path: the path to delete.
        """
        self.client.delete_objects(
            Bucket=self.bucket,
            Delete={"Objects": [{"Key": file_path}]},
        )

    def list_all_files(self, *, with_prefix: bool = True) -> Generator[str, None, None]:
        """List all files in the backend.

        Args:
            with_prefix: Whether to include the prefix in the lookup.

        Yields:
            The path to each file in the backend.
        """
        kwargs: dict[str, t.Any] = {"Bucket": self.bucket}
        if with_prefix:
            kwargs["Prefix"] = self.prefix

        for state_obj in self.client.list_objects_v2(**kwargs).get("Contents", []):
            yield state_obj["Key"]

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
