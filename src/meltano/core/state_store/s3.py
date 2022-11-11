"""StateStoreManager for S3 cloud storage backend."""
from __future__ import annotations

import re

from meltano.core.state_store.filesystem import (
    BaseFilesystemStateStoreManager,
    InvalidStateBackendConfigurationException,
)


class S3StateStoreManager(BaseFilesystemStateStoreManager):
    """State backend for S3."""

    label: str = "AWS S3"

    def __init__(
        self,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        bucket: str | None = None,
        prefix: str | None = None,
        endpoint_url: str | None = None,
        **kwargs,
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
        self.bucket = bucket or self.parsed.hostname
        self.prefix = prefix or self.parsed.path
        self.endpoint_url = endpoint_url
        self._client = None

    @staticmethod
    def is_file_not_found_error(err: Exception) -> bool:
        """Check if err is equivalent to file not being found.

        Args:
            err: the err to check

        Returns:
            True if error represents file not being found, else False
        """
        return (
            isinstance(err, OSError)
            and "NoSuchKey" in err.args[0]
            or (isinstance(err, KeyError) and "ActualObjectSize" in err.args[0])
        )

    @property
    def client(self):
        """Get an authenticated boto3.Client.

        Returns:
            A boto3.Client.

        Raises:
            InvalidStateBackendConfigurationException: when configured AWS settings are invalid.
        """
        if not self._client:
            if self.aws_secret_access_key and self.aws_access_key_id:
                from boto3 import Session

                session = Session(
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                )
                self._client = session.client("s3", endpoint_url=self.endpoint_url)
            elif self.aws_secret_access_key and not self.aws_access_key_id:
                raise InvalidStateBackendConfigurationException(
                    "AWS secret access key configured, but not AWS access key ID."
                )
            elif self.aws_access_key_id and not self.aws_secret_access_key:
                raise InvalidStateBackendConfigurationException(
                    "AWS access key ID configured, but no AWS secret access key."
                )
        return self._client

    @property
    def state_dir(self) -> str:
        """Get the prefix that state should be stored at.

        Returns:
            The relevant prefix
        """
        return self.prefix.lstrip(self.delimiter).rstrip(self.delimiter)

    def get_state_ids(self, pattern: str | None = None):
        """Get list of state_ids stored in the backend.

        Args:
            pattern: glob-style pattern to filter state_ids by

        Returns:
            List of state_ids
        """
        if pattern:
            pattern_re = re.compile(pattern.replace("*", ".*"))
        state_ids = set()
        for state_obj in self.client.list_objects_v2(
            Bucket=self.bucket, Prefix=self.prefix
        ).get("Contents", []):
            (state_id, filename) = state_obj["Key"].split("/")[-2:]
            if filename == "state.json":
                if not pattern:
                    state_ids.add(
                        state_id.replace(self.prefix, "").replace("/state.json", "")
                    )
                elif pattern_re.match(state_id):
                    state_ids.add(state_id)
        return list(state_ids)

    def delete(self, file_path: str):
        """Delete the file/blob at the given path.

        Args:
            file_path: the path to delete.
        """
        self.client.delete_objects(
            Bucket=self.bucket,
            Delete={"Objects": [{"Key": file_path}]},
        )
