"""StateStoreManager for Google Cloud storage backend."""

from __future__ import annotations

import json
import typing as t
import warnings
from functools import cached_property

import google
import google.api_core.exceptions
import google.cloud.storage
import structlog.stdlib

from meltano.core.state_store.filesystem import CloudStateStoreManager

if t.TYPE_CHECKING:
    from collections.abc import Generator

logger = structlog.stdlib.get_logger(__name__)


class GCSStateStoreManager(CloudStateStoreManager):
    """State backend for Google Cloud Storage."""

    label = "Google Cloud Storage"

    def __init__(
        self,
        bucket: str | None = None,
        prefix: str | None = None,
        application_credentials: str | None = None,
        application_credentials_path: str | None = None,
        application_credentials_json: str | None = None,
        **kwargs: t.Any,
    ):
        """Initialize the BaseFilesystemStateStoreManager.

        Args:
            bucket: the bucket to store state in
            prefix: the prefix to store state at
            application_credentials_path: Path to a Google service account JSON file.
            application_credentials_json: Raw JSON string of service account
                credentials.
            application_credentials: Deprecated. Use application_credentials_path
                instead.
            kwargs: additional keyword args to pass to parent

        Precedence:
            1. If both application_credentials_path and application_credentials_json are
               provided, raises an error.
            2. If only application_credentials_json is provided, it is used.
            3. If only application_credentials_path is provided, it is used.
            4. If only application_credentials (deprecated) is provided, it is used as
               application_credentials_path.

        Raises:
            ValueError: If both application_credentials_path and
                application_credentials_json are provided.
        """
        super().__init__(**kwargs)
        self.bucket = bucket or self.parsed.hostname
        self.prefix = prefix or self.parsed.path

        # Handle backwards compatibility and deprecation warning
        if application_credentials is not None:
            warnings.warn(
                "The 'application_credentials' parameter is deprecated. "
                "Use 'application_credentials_path' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            if application_credentials_path is None:
                application_credentials_path = application_credentials

        if application_credentials_path and application_credentials_json:
            msg = "Provide only one of 'application_credentials_path' or 'application_credentials_json', not both."  # noqa: E501
            raise ValueError(msg)

        self.application_credentials_path = application_credentials_path
        self.application_credentials_json = application_credentials_json

    @staticmethod
    def is_file_not_found_error(err: Exception) -> bool:
        """Check if err is equivalent to file not being found.

        Args:
            err: the err to check

        Returns:
            True if error represents file not being found, else False
        """
        return isinstance(err, google.api_core.exceptions.NotFound) and (
            "No such object:" in err.args[0] or "blob" in err.args[0]
        )

    @cached_property
    def client(self) -> google.cloud.storage.Client:
        """Get an authenticated google.cloud.storage.Client.

        Returns:
            A google.cloud.storage.Client.
        """
        if self.application_credentials_json:
            # Parse JSON string and create client from service account info
            try:
                credentials_info = json.loads(self.application_credentials_json)
            except json.JSONDecodeError as e:
                msg = (
                    "Invalid JSON in application_credentials_json: "
                    f"{e.doc[max(e.pos - 9, 0) : e.pos + 10]}"
                )
                raise ValueError(msg) from e
            return google.cloud.storage.Client.from_service_account_info(
                credentials_info,
            )
        if self.application_credentials_path:
            # Use existing file-based authentication
            return google.cloud.storage.Client.from_service_account_json(
                self.application_credentials_path,
            )
        # Use default authentication in environment
        return google.cloud.storage.Client()

    @property
    def extra_transport_params(self) -> dict[str, t.Any]:
        """Extra transport params for ``smart_open.open``."""
        return {
            "blob_properties": {
                "content_type": "application/json",
            },
        }

    def delete_file(self, file_path: str) -> None:
        """Delete the file/blob at the given path.

        Args:
            file_path: the path to delete.

        Raises:
            Exception: if error not indicating file is not found is thrown
        """
        bucket = self.client.bucket(self.bucket)
        try:
            blob = bucket.blob(file_path)
            blob.delete()
        except Exception as e:
            if self.is_file_not_found_error(e):
                logger.debug("File not found: %s", file_path, exc_info=e)
            else:
                raise e  # noqa: TRY201

    def list_all_files(self, *, with_prefix: bool = True) -> Generator[str, None, None]:
        """List all files in the backend.

        Args:
            with_prefix: Whether to include the prefix in the lookup.

        Yields:
            The next file in the backend.
        """
        blob: google.cloud.storage.Blob
        for blob in self.client.list_blobs(
            bucket_or_name=self.bucket,
            prefix=self.state_dir if with_prefix else None,
        ):
            yield blob.name

    def copy_file(self, src: str, dst: str) -> None:
        """Copy a file from one location to another.

        Args:
            src: the source path
            dst: the destination path
        """
        bucket = self.client.bucket(self.bucket)
        blob = bucket.blob(src)
        bucket.copy_blob(blob, bucket, dst)
