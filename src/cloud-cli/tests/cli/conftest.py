from __future__ import annotations

import typing as t

import pytest

from meltano.cloud.api import MeltanoCloudClient

if t.TYPE_CHECKING:
    from meltano.cloud.api.config import MeltanoCloudConfig


@pytest.fixture()
def client(config: MeltanoCloudConfig) -> MeltanoCloudClient:
    """Return a MeltanoCloudClient instance with fake credentials."""
    return MeltanoCloudClient(config=config)
