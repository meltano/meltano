"""StateStoreManager for Azure Blob storage backend."""
from __future__ import annotations

import re
import sys
from collections.abc import Iterator
from contextlib import contextmanager

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from cached_property import cached_property

from meltano.core.state_store.filesystem import CloudStateStoreManager

try:
    from azure.storage.blob import BlobServiceClient  # type: ignore
except ImportError:
    BlobServiceClient = None


class MissingAzureError(Exception):
    """Raised when azure is required but no installed."""

    def __init__(self):
        """Initialize a MissingAzureError."""
        super().__init__(
            "azure required but not installed. Install meltano[azure] to use Azure Blob Storage as a state backend.",  # noqa: E501
        )


@contextmanager
def requires_azure():
    """Raise MissingAzureError if azure is required but missing in context.

    Raises:
        MissingAzureError: if azure is not installed.

    Yields:
        None
    """
    if not BlobServiceClient:
        raise MissingAzureError
    yield


class AZStorageStateStoreManager(CloudStateStoreManager):
    """State backend for Azure Blob Storage."""

    label: str = "Azure Blob Storage"

    def __init__(
        self,
        container_name: str | None = None,
        connection_string: str | None = None,
        prefix: str | None = None,
        **kwargs,
    ):
        """Initialize the BaseFilesystemStateStoreManager.

        Args:
            container_name: the container to store state in.
            connection_string: connection string to use in authenticating to Azure
            prefix: the prefix to store state at
            kwargs: additional keyword args to pass to parent
        """
        super().__init__(**kwargs)
        self.connection_string = connection_string
        self.container_name = container_name or self.parsed.hostname
        self.prefix = prefix or self.parsed.path

    @staticmethod
    def is_file_not_found_error(err: Exception) -> bool:
        """Check if err is equivalent to file not being found.

        Args:
            err: the err to check

        Returns:
            True if error represents file not being found, else False
        """
        from azure.core.exceptions import ResourceNotFoundError  # type: ignore

        return (
            isinstance(err, ResourceNotFoundError)
            and "ErrorCode:BlobNotFound" in err.args[0]
        )

    @cached_property
    def client(self):
        """Get an authenticated azure.storage.blob.BlobServiceClient.

        Returns:
            An authenticated azure.storage.blob.BlobServiceClient
        """
        with requires_azure():
            if self.connection_string:
                return BlobServiceClient.from_connection_string(self.connection_string)
            return BlobServiceClient()

    def delete(self, file_path: str):
        """Delete the file/blob at the given path.

        Args:
            file_path: the path to delete.

        Raises:
            Exception: if error not indicating file is not found is thrown
        """
        blob_client = self.client.get_blob_client(
            container=self.container_name,
            blob=file_path,
        )
        try:
            blob_client.delete_blob()
        except Exception as e:
            if not self.is_file_not_found_error(e):
                raise e

    def list_all_files(self) -> Iterator[str]:
        """List all files in the backend.

        Yields:
            The next file in the backend.
        """
        container_client = self.client.get_container_client(self.container_name)
        for blob in container_client.list_blobs(
            name_starts_with=self.prefix.lstrip("/"),
        ):
            yield blob.name

    def copy_file(self, src: str, dst: str) -> None:
        """Copy a file from one location to another.

        Args:
            src: the source path
            dst: the destination path
        """
        # TODO
        container_client = self.client.get_container_client(self.container_name)
        container_client.start_copy_from_url(
            src,
            dst,
        )
