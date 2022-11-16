"""StateStoreManager for Google Cloud storage backend."""
from __future__ import annotations

import re

from meltano.core.state_store.filesystem import BaseFilesystemStateStoreManager


class GCSStateStoreManager(BaseFilesystemStateStoreManager):
    """State backend for Google Cloud Storage."""

    label: str = "Google Cloud Storage"

    def __init__(
        self,
        bucket: str | None = None,
        prefix: str | None = None,
        application_credentials: str | None = None,
        **kwargs,
    ):
        """Initialize the BaseFilesystemStateStoreManager.

        Args:
            bucket: the bucket to store state in
            prefix: the prefix to store state at
            application_credentials: application credentials to  use in authenticating to GCS
            kwargs: additional keyword args to pass to parent
        """
        super().__init__(**kwargs)
        self._client = None
        self.bucket = bucket or self.parsed.hostname
        self.prefix = prefix or self.parsed.path
        self.application_credentials = application_credentials

    @staticmethod
    def is_file_not_found_error(err: Exception) -> bool:
        """Check if err is equivalent to file not being found.

        Args:
            err: the err to check

        Returns:
            True if error represents file not being found, else False
        """
        from google.api_core.exceptions import NotFound  # type: ignore

        return isinstance(err, NotFound) and (
            "No such object:" in err.args[0] or "blob" in err.args[0]
        )

    @property
    def client(self):
        """Get an authenticated google.cloud.storage.Client.

        Returns:
            A google.cloud.storage.Client.
        """
        if not self._client:
            from google.cloud.storage import Client  # type: ignore

            if self.application_credentials:
                self._client = Client.from_service_account_json(
                    self.application_credentials
                )
            else:
                # Use default authentication in environment
                self._client = Client()
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
        for blob in self.client.list_blobs(bucket_or_name=self.bucket):
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
        bucket = self.client.bucket(self.bucket)
        try:
            blob = bucket.blob(file_path)
            blob.delete()
        except Exception as e:
            if self.is_file_not_found_error(e):
                ...
            else:
                raise e
