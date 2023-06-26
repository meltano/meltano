from __future__ import annotations

import os
from pathlib import Path

import jwt
import pytest
from pytest_httpserver import HTTPServer
from pytest_structlog import StructuredLogCapture

from meltano.cloud.api.config import MeltanoCloudConfig


@pytest.fixture(autouse=True)
def unset_env_vars(monkeypatch: pytest.MonkeyPatch):
    """Unsets possible env variables set during development while using Meltano Cloud.

    MeltanoCloudConfig __getattribute__ overrides the config value on get
    to env vars if set. This causes tests to fail unless you unset the env variables.
    """
    monkeypatch.delenv("MELTANO_CLOUD_BASE_URL", raising=False)
    monkeypatch.delenv("MELTANO_CLOUD_BASE_AUTH_URL", raising=False)
    monkeypatch.delenv("MELTANO_CLOUD_APP_CLIENT_ID", raising=False)
    monkeypatch.delenv("MELTANO_CLOUD_TENANT_RESOURCE_KEY", raising=False)


@pytest.fixture(scope="session", autouse=True)
def config_path(tmpdir_factory: pytest.TempdirFactory) -> Path:
    """Return the path to the test configuration file."""
    directory = Path(tmpdir_factory.mktemp("test_config"))
    filepath = Path(directory).joinpath("config.json")
    filepath.touch()
    os.environ["MELTANO_CLOUD_CONFIG_PATH"] = str(filepath)
    return filepath


# Define this fixture to make all tests auto-use the structlog capture fixture.
# This ensures that log messages are not mixed with other output, yet can still
# be tested.
@pytest.fixture(autouse=True)
def log(log: StructuredLogCapture) -> StructuredLogCapture:
    return log


@pytest.fixture(scope="session", autouse=True)
def httpserver() -> HTTPServer:
    with HTTPServer() as http_server:
        http_server.expect_request("/oauth2/userInfo").respond_with_json(
            {"sub": "meltano-cloud-test"},
        )
        yield http_server


@pytest.fixture(autouse=True)
def clear_httpserver_log(httpserver: HTTPServer) -> None:
    httpserver.clear_log()


@pytest.fixture(autouse=True)
def clear_httpserver_tmp_hanlders(httpserver: HTTPServer) -> None:
    httpserver.oneshot_handlers.clear()
    httpserver.ordered_handlers.clear()


@pytest.fixture()
def auth_token():
    return "meltano-cloud-test"


@pytest.fixture()
def id_token(tenant_resource_key: str, internal_project_id: str, auth_token: str):
    """Return a fake ID token.

    Includes the tenant_resource_key and internal_project_id as a custom attribute.
    """
    return jwt.encode(
        {
            "sub": auth_token,
            "custom:trk_and_pid": f"{tenant_resource_key}::{internal_project_id}",
        },
        key="",
    )


@pytest.fixture(scope="session")
def httpserver_base_url(httpserver: HTTPServer) -> str:
    return httpserver.url_for("")


@pytest.fixture()
def config(
    config_path: Path,
    id_token: str,
    httpserver_base_url: str,
) -> MeltanoCloudConfig:
    """Return a MeltanoCloudConfig instance with fake credentials."""
    config = MeltanoCloudConfig(  # noqa: S106
        config_path=config_path,
        base_auth_url=httpserver_base_url,
        base_url=httpserver_base_url,
        app_client_id="meltano-cloud-test",
        access_token="meltano-cloud-test",  # noqa: S106
        id_token=id_token,
    )
    config.write_to_file()
    return config
