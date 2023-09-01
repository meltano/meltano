from __future__ import annotations

import json
from http import HTTPStatus
from pathlib import Path

import pytest
from aiohttp import web

from meltano.cloud.api.auth import MeltanoCloudAuth
from meltano.cloud.api.config import MeltanoCloudConfig


class TestMeltanoCloudAuthCallbackServer:
    """Test the Meltano Cloud Auth Callback Server."""

    @pytest.fixture()
    def config(self, tmp_path: Path):
        return MeltanoCloudConfig(config_path=tmp_path / "meltano-cloud.json")

    @pytest.fixture()
    async def client(
        self,
        config: MeltanoCloudConfig,
        aiohttp_client,
    ) -> web.Application:
        async with MeltanoCloudAuth(config).callback_server() as app:
            yield await aiohttp_client(app)

    async def test_callback_page(self, client: web.Application):
        response = await client.get("/")
        assert (
            '<p id="start-message">Logging in to Meltano Cloud...</p>'
            in await response.text()
        )

    async def test_handle_tokens(
        self,
        client: web.Application,
        config: MeltanoCloudConfig,
    ):
        response = await client.get(
            "/tokens?id_token=meltano-cloud-testing&access_token=meltano-cloud-testing",
        )
        config.refresh()
        assert response.status == HTTPStatus.NO_CONTENT
        assert config.access_token == "meltano-cloud-testing"  # noqa: S105
        assert config.id_token == "meltano-cloud-testing"  # noqa: S105
        with Path(config.config_path).open() as config_file:
            config_on_disk = json.load(config_file)
        assert config_on_disk["access_token"] == "meltano-cloud-testing"
        assert config_on_disk["id_token"] == "meltano-cloud-testing"

    async def test_handle_logout(
        self,
        client: web.Application,
        config: MeltanoCloudConfig,
    ):
        config.access_token = "meltano-cloud-testing"  # noqa: S105
        config.id_token = "meltano-cloud-testing"  # noqa: S105
        config.write_to_file()
        response = await client.get("/logout")
        assert response.status == HTTPStatus.OK
        config.refresh()
        assert config.id_token is None
        assert config.access_token is None
        with Path(config.config_path).open() as config_file:
            config_on_disk = json.load(config_file)
        assert config_on_disk.get("access_token") is None
        assert config_on_disk.get("id_token") is None
