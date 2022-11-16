"""StateStoreManager for Azure Blob storage backend."""
from __future__ import annotations

import re

from meltano.core.state_store.filesystem import BaseFilesystemStateStoreManager


class AZStorageStateStoreManager(BaseFilesystemStateStoreManager):
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
        self._client = None

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

    @property
    def client(self):
        """Get an authenticated azure.storage.blob.BlobServiceClient.

        Returns:
            An authenticated azure.storage.blob.BlobServiceClient
        """
        if self.connection_string and not self._client:
            from azure.storage.blob import BlobServiceClient  # type: ignore

            self._client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
        return self._client

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
            name_starts_with=self.prefix.lstrip("/")
        ):
            (state_id, filename) = blob.name.split("/")[-2:]
            if filename == "state.json":
                if not pattern:
                    state_ids.add(state_id)
                elif pattern_re.match(state_id):
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
            container=self.container_name, blob=file_path
        )
        try:
            blob_client.delete_blob()
        except Exception as e:
            if self.is_file_not_found_error(e):
                ...
            else:
                raise e
