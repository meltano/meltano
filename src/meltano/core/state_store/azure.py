"""StateStoreManager for Azure Blob storage backend."""
from __future__ import annotations

import re
import sys
from contextlib import contextmanager

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from cached_property import cached_property

from meltano.core.error import MeltanoError
from meltano.core.state_store.filesystem import BaseFilesystemStateStoreManager

AZURE_INSTALLED = True

try:
    from azure.storage.blob import BlobServiceClient
except ImportError:
    AZURE_INSTALLED = False


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
    if not AZURE_INSTALLED:
        raise MissingAzureError
    yield


class AZStorageStateStoreManager(BaseFilesystemStateStoreManager):
    """State backend for Azure Blob Storage."""

    label: str = "Azure Blob Storage"

    def __init__(
        self,
        connection_string: str | None = None,
        prefix: str | None = None,
        **kwargs,
    ):
        """Initialize the BaseFilesystemStateStoreManager.

        Args:
            connection_string: connection string to use in authenticating to Azure
            prefix: the prefix to store state at
            kwargs: additional keyword args to pass to parent

        Raises:
            MeltanoError: If container name is not included in the URI.
        """
        super().__init__(**kwargs)
        self.connection_string = connection_string

        if not self.parsed.hostname:
            raise MeltanoError(
                f"Azure state backend URI must include a container name: {self.uri}",
                "Verify state backend URI. Must be in the form of azure://<container>/<prefix>",  # noqa: E501
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
            if self.connection_string:
                return BlobServiceClient.from_connection_string(self.connection_string)

            raise MeltanoError(
                "Azure state backend requires a connection string",
                "Read https://learn.microsoft.com/en-us/azure/storage/common/storage-configure-connection-string for more information.",  # noqa: E501
            )

    @property
    def state_dir(self) -> str:
        """Get the prefix that state should be stored at.

        Returns:
            The relevant prefix
        """
        return self.prefix.lstrip(self.delimiter).rstrip(self.delimiter)

    def get_state_ids(self, pattern: str | None = None):  # noqa: WPS210
        """Get list of state_ids stored in the backend.

        Args:
            pattern: glob-style pattern to filter state_ids by

        Returns:
            List of state_ids
        """
        if pattern:
            pattern_re = re.compile(pattern.replace("*", ".*"))
        state_ids = set()
        container_client = self.client.get_container_client(self.container_name)
        for blob in container_client.list_blobs(
            name_starts_with=self.prefix.lstrip("/"),
        ):
            (state_id, filename) = blob.name.split("/")[-2:]
            if filename == "state.json" and (not pattern) or pattern_re.match(state_id):
                state_ids.add(state_id)
        return list(state_ids)

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
