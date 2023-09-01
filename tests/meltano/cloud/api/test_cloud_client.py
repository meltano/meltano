"""Test the Meltano Cloud API client."""

from __future__ import annotations

import re
import typing as t
from http import HTTPStatus

import mock
import pytest
from mock import AsyncMock, MagicMock

from meltano.cloud.api.client import MeltanoCloudClient, MeltanoCloudError
from meltano.cloud.api.config import MeltanoCloudConfig

if t.TYPE_CHECKING:
    from pytest_httpserver import HTTPServer


class TestMeltanoCloudClient:
    """Test the Meltano Cloud API client."""

    @pytest.fixture()
    def login_mock(self, config: MeltanoCloudConfig):
        def set_auth_tokens():
            config.id_token = "fake_id_token"  # noqa: S105
            config.access_token = "fake_access_token"  # noqa: S105

        with mock.patch("meltano.cloud.api.auth.MeltanoCloudAuth.login") as login_mock:
            login_mock.return_value = None
            login_mock.side_effect = set_auth_tokens
            yield login_mock

    @pytest.mark.asyncio()
    async def test_authenticated_context(
        self,
        config: MeltanoCloudConfig,
        login_mock: MagicMock | AsyncMock,
    ):
        config.id_token = None
        config.access_token = None
        async with MeltanoCloudClient(config) as client:
            assert not client.auth.has_auth_tokens()

            # Expect login to get called if no auth tokens have been cached
            async with client.authenticated():
                login_mock.assert_awaited_once()
                assert client.auth.has_auth_tokens()
                assert (
                    client._session.headers["Authorization"] == "Bearer fake_id_token"
                )
            assert "Authorization" not in client._session.headers

            # Expect login to not get called if auth tokens have been cached
            login_mock.reset_mock()
            async with client.authenticated():
                login_mock.assert_not_called()
                assert client.auth.has_auth_tokens()
                assert (
                    client._session.headers["Authorization"] == "Bearer fake_id_token"
                )
            assert "Authorization" not in client._session.headers

    @pytest.mark.asyncio()
    async def test_no_login_on_403(
        self,
        config: MeltanoCloudConfig,
        login_mock: MagicMock | AsyncMock,
        httpserver: HTTPServer,
    ):
        # Expect 403 response to cause an error if outside of an authenticated context
        path = "/fakeRequest"
        pattern = re.compile(f"^{path}(\\?.*)?$")
        httpserver.expect_oneshot_request(pattern).respond_with_data(
            status=HTTPStatus.FORBIDDEN,
        )
        async with MeltanoCloudClient(config) as client:
            with pytest.raises(MeltanoCloudError) as excinfo:
                async with client._raw_request("GET", "/fakeRequest"):  # noqa: WPS328
                    pass
            assert excinfo.value.response.status == 403
            login_mock.assert_not_called()

    @pytest.mark.asyncio()
    async def test_authenticated_context_login_on_403(
        self,
        config: MeltanoCloudConfig,
        login_mock: MagicMock | AsyncMock,
        httpserver: HTTPServer,
    ):
        path = "/fakeRequest"
        pattern = re.compile(f"^{path}(\\?.*)?$")
        httpserver.expect_oneshot_request(pattern).respond_with_data(
            status=HTTPStatus.FORBIDDEN,
        )
        httpserver.expect_oneshot_request(pattern).respond_with_data(
            status=HTTPStatus.OK,
        )
        async with MeltanoCloudClient(config) as client, client.authenticated():
            async with client._raw_request("GET", "/fakeRequest") as response:
                assert response.status == HTTPStatus.OK
            login_mock.assert_awaited_once()

    @pytest.mark.asyncio()
    async def test_authenticated_context_failure_on_retry(
        self,
        config: MeltanoCloudConfig,
        login_mock: MagicMock | AsyncMock,
        httpserver: HTTPServer,
    ):
        path = "/fakeRequest"
        pattern = re.compile(f"^{path}(\\?.*)?$")
        httpserver.expect_oneshot_request(pattern).respond_with_data(
            status=HTTPStatus.FORBIDDEN,
        )
        httpserver.expect_oneshot_request(pattern).respond_with_data(
            status=HTTPStatus.FORBIDDEN,
        )
        async with MeltanoCloudClient(config) as client, client.authenticated():
            with pytest.raises(MeltanoCloudError) as excinfo:
                async with client._raw_request(  # noqa: WPS328
                    "GET",
                    "/fakeRequest",
                ):
                    pass
            assert excinfo.value.response.status == 403
            login_mock.assert_awaited_once()
