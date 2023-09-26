"""StateStoreManager for Google Cloud storage backend."""
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from functools import cached_property

from meltano.core.state_store.filesystem import CloudStateStoreManager

GOOGLE_INSTALLED = True

try:
    import google  # type: ignore
except ImportError:
    GOOGLE_INSTALLED = False


class MissingGoogleError(Exception):
    """Raised when google is required but not installed."""

    def __init__(self):
        """Initialize a MissingGoogleError."""
        super().__init__(
            "google-cloud-storage required but not installed. Install meltano[gcs] to use GCS as a state backend.",  # noqa: E501
        )


@contextmanager
def requires_gcs():
    """Raise MissingGoogleError if gcs is required but missing in context.

    Raises:
        MissingGoogleError: if google-cloud-storage is not installed.

    Yields:
        None
    """
    if not GOOGLE_INSTALLED:
        raise MissingGoogleError
    yield


class GCSStateStoreManager(CloudStateStoreManager):
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
            application_credentials: application credentials to use in
                authenticating to GCS
            kwargs: additional keyword args to pass to parent
        """
        super().__init__(**kwargs)
        self.bucket = bucket or self.parsed.hostname
        self.prefix = prefix or self.parsed.path
        self.application_credentials = application_credentials

    @staticmethod
    @requires_gcs()
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
    def client(self):
        """Get an authenticated google.cloud.storage.Client.

        Returns:
            A google.cloud.storage.Client.
        """
        with requires_gcs():
            if self.application_credentials:
                return google.cloud.storage.Client.from_service_account_json(
                    self.application_credentials,
                )
            # Use default authentication in environment
            return google.cloud.storage.Client()

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

    def list_all_files(self) -> Iterator[str]:
        """List all files in the backend.

        Yields:
            The next file in the backend.
        """
        for blob in self.client.list_blobs(bucket_or_name=self.bucket):  # noqa: WPS526
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
