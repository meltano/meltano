"""StateStoreManager for Azure Blob storage backend."""

from __future__ import annotations

import typing as t
from contextlib import contextmanager
from functools import cached_property

from meltano.core.error import MeltanoError
from meltano.core.state_store.filesystem import (
    CloudStateStoreManager,
)

if t.TYPE_CHECKING:
    from collections.abc import Generator

AZURE_INSTALLED = True

try:
    from azure.storage.blob import BlobServiceClient
except ImportError:
    AZURE_INSTALLED = False


class MissingAzureError(Exception):
    """Raised when azure is required but no installed."""

    def __init__(self) -> None:
        """Initialize a MissingAzureError."""
        super().__init__(
            "azure required but not installed. Install meltano[azure] to use Azure Blob Storage as a state backend.",  # noqa: E501
        )


@contextmanager
def requires_azure() -> Generator[None, None, None]:
    """Raise MissingAzureError if azure is required but missing in context.

    Raises:
        MissingAzureError: if azure is not installed.

    Yields:
        None
    """
    if not AZURE_INSTALLED:
        raise MissingAzureError
    yield


class AZStorageStateStoreManager(CloudStateStoreManager):
    """State backend for Azure Blob Storage."""

    label: str = "Azure Blob Storage"

    def __init__(
        self,
        connection_string: str | None = None,
        prefix: str | None = None,
        storage_account_url: str | None = None,
        **kwargs: t.Any,
    ):
        """Initialize the BaseFilesystemStateStoreManager.

        Args:
            connection_string: connection string to use in authenticating to Azure
            prefix: the prefix to store state at
            storage_account_url: url of the azure stroga account
            kwargs: additional keyword args to pass to parent

        Raises:
            MeltanoError: If container name is not included in the URI.
        """
        super().__init__(**kwargs)
        self.connection_string = connection_string
        self.storage_account_url = storage_account_url

        if not self.parsed.hostname:
            raise MeltanoError(
                f"Azure state backend URI must include a container name: {self.uri}",  # noqa: EM102
                "Verify state backend URI. Must be in the form of azure://<container>/<prefix>",
            )

        self.container_name = self.parsed.hostname
        self.prefix = prefix or self.parsed.path

    @staticmethod
    def is_file_not_found_error(err: Exception) -> bool:
        """Check if err is equivalent to file not being found.

        Args:
            err: the err to check

        Returns:
            True if error represents file not being found, else False
        """
        from azure.core.exceptions import ResourceNotFoundError

        return (
            isinstance(err, ResourceNotFoundError)
            and "ErrorCode:BlobNotFound" in err.args[0]
        )

    @cached_property
    def client(self) -> BlobServiceClient:
        """Get an authenticated azure.storage.blob.BlobServiceClient.

        Returns:
            An authenticated azure.storage.blob.BlobServiceClient

        Raises:
            MeltanoError: If connection string is not provided.
        """
        with requires_azure():
            if self.storage_account_url:
                from azure.identity import DefaultAzureCredential

                default_credential = DefaultAzureCredential()
                return BlobServiceClient(
                    self.storage_account_url,
                    credential=default_credential,
                )

            if self.connection_string:
                return BlobServiceClient.from_connection_string(self.connection_string)

            raise MeltanoError(
                "Azure state backend requires a connection string "  # noqa: EM101
                "or an account URL to use host credentials",
                "Read https://learn.microsoft.com/en-us/azure/storage/common/storage-configure-connection-string for more information.",  # noqa: E501
            )

    def delete(self, file_path: str) -> None:
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

    def list_all_files(
        self,
        *,
        with_prefix: bool = True,
    ) -> t.Generator[str, None, None]:
        """List all files in the backend.

        Args:
            with_prefix: Whether to include the prefix in the lookup.

        Yields:
            The next file in the backend.
        """
        container_client = self.client.get_container_client(self.container_name)
        for blob in container_client.list_blobs(
            name_starts_with=self.prefix.lstrip("/") if with_prefix else None,
        ):
            yield blob.name

    def copy_file(self, src: str, dst: str) -> None:
        """Copy a file from one location to another.

        Args:
            src: the source path
            dst: the destination path
        """
        container_client = self.client.get_container_client(self.container_name)
        src_blob_client = container_client.get_blob_client(src)
        dst_blob_client = container_client.get_blob_client(dst)
        dst_blob_client.start_copy_from_url(src_blob_client.url)
