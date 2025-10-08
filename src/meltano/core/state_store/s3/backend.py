"""StateStoreManager for S3 cloud storage backend."""

from __future__ import annotations

import dataclasses
import sys
import typing as t

from upath.implementations.cloud import S3Path

from meltano.core.state_store.filesystem import (
    FSSpecStateStoreManager,
    InvalidStateBackendConfigurationException,
)

if sys.version_info >= (3, 12):
    from typing import override  # noqa: ICN003
else:
    from typing_extensions import override


@dataclasses.dataclass
class S3StateStoreManager(FSSpecStateStoreManager[S3Path]):
    """State backend for S3."""

    label: t.ClassVar[str] = "AWS S3"

    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    endpoint_url: str | None = None

    def __post_init__(self) -> None:
        """Post-initialize the S3StateStoreManager."""
        super().__post_init__()
        self.aws_access_key_id = self.aws_access_key_id or self._parsed.username
        self.aws_secret_access_key = self.aws_secret_access_key or self._parsed.password

    @override
    def get_upath(self) -> S3Path:
        """Get the UPath instance for the state store manager."""
        if self.aws_access_key_id is None and self.aws_secret_access_key is not None:
            msg = "AWS secret access key configured, but not AWS access key ID."
            raise InvalidStateBackendConfigurationException(msg)
        if self.aws_secret_access_key is None and self.aws_access_key_id is not None:
            msg = "AWS access key ID configured, but no AWS secret access key."
            raise InvalidStateBackendConfigurationException(msg)

        return S3Path.from_uri(
            self.uri,
            key=self.aws_access_key_id,
            secret=self.aws_secret_access_key,
            endpoint_url=self.endpoint_url,
        )
