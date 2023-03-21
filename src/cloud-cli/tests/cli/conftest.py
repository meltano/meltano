from __future__ import annotations

from pathlib import Path

import jwt
import pytest

from meltano.cloud.api import MeltanoCloudClient
from meltano.cloud.api.config import MeltanoCloudConfig


@pytest.fixture
def tenant_resource_key():
    """Return a fake tenant resource key."""
    return "meltano-cloud-test"


@pytest.fixture
def internal_project_id():
    """Return a fake Cloud/internal project ID."""
    return "pytest-123"


@pytest.fixture
def deployment():
    """Return a fake deployment ID."""
    return "sandbox"


@pytest.fixture
def job_or_schedule():
    """Return a fake job or schedule name."""
    return "daily"


@pytest.fixture
def id_token(tenant_resource_key: str, internal_project_id: str):
    """Return a fake ID token.

    Includes the tenant_resource_key and internal_project_id as a custom attribute.
    """
    return jwt.encode(
        {
            "sub": "meltano-cloud-test",
            "custom:trk_and_pid": f"{tenant_resource_key}::{internal_project_id}",
        },
        key="",
    )


@pytest.fixture
def config(config_path: Path, id_token: str):
    """Return a MeltanoCloudConfig instance with fake credentials."""
    config = MeltanoCloudConfig(  # noqa: S106
        config_path=config_path,
        base_auth_url="http://auth-test.meltano.cloud",
        base_url="https://internal.api-test.meltano.cloud/",
        app_client_id="meltano-cloud-test",
        access_token="meltano-cloud-test",  # noqa: S106
        id_token=id_token,
    )
    config.write_to_file()
    return config


@pytest.fixture
def client(config: MeltanoCloudConfig):
    """Return a MeltanoCloudClient instance with fake credentials."""
    return MeltanoCloudClient(config=config)
