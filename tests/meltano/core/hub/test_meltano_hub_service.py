from __future__ import annotations

import typing as t
from unittest import mock

import click
import pytest
from requests import HTTPError, Response
from requests.adapters import BaseAdapter

from meltano.cli import cli
from meltano.cli.hub import hub
from meltano.core.hub.client import HubConnectionError, HubPluginVariantNotFoundError
from meltano.core.plugin.base import PluginType, Variant
from meltano.core.plugin.error import PluginNotFoundError

if t.TYPE_CHECKING:
    from collections import Counter

    from meltano.core.project import Project


class TestMeltanoHubService:
    def test_find_definition_specified_variant(
        self,
        project: Project,
        hub_request_counter: Counter,
    ) -> None:
        definition = project.hub_service.find_definition(
            PluginType.EXTRACTORS,
            "tap-mock",
            variant_name="meltano",
        )
        assert definition.name == "tap-mock"
        assert definition.variants[0].name == "meltano"

        assert hub_request_counter["/extractors/index"] == 1
        assert hub_request_counter["/extractors/tap-mock--meltano"] == 1

    def test_find_definition_default_variant(
        self,
        project: Project,
        hub_request_counter: Counter,
    ) -> None:
        definition = project.hub_service.find_definition(
            PluginType.EXTRACTORS,
            "tap-mock",
        )
        assert definition.name == "tap-mock"
        assert definition.variants[0].name == "meltano"

        assert hub_request_counter["/extractors/index"] == 1
        assert hub_request_counter["/extractors/tap-mock--meltano"] == 1

    def test_find_definition_original_variant(
        self,
        project: Project,
        hub_request_counter: Counter,
    ) -> None:
        definition = project.hub_service.find_definition(
            PluginType.EXTRACTORS,
            "tap-mock",
            variant_name=Variant.ORIGINAL_NAME,
        )
        assert definition.name == "tap-mock"
        assert definition.variants[0].name == "meltano"

        assert hub_request_counter["/extractors/index"] == 1
        assert hub_request_counter["/extractors/tap-mock--meltano"] == 1

    def test_definition_not_found(
        self,
        project: Project,
        hub_request_counter: Counter,
    ) -> None:
        with pytest.raises(PluginNotFoundError):
            project.hub_service.find_definition(PluginType.EXTRACTORS, "tap-not-found")

        assert hub_request_counter["/extractors/index"] == 1
        assert len(hub_request_counter) == 1

    def test_variant_not_found(
        self,
        project: Project,
        hub_request_counter: Counter,
    ) -> None:
        with pytest.raises(HubPluginVariantNotFoundError):
            project.hub_service.find_definition(
                PluginType.EXTRACTORS,
                "tap-mock",
                "not-found",
            )

        assert hub_request_counter["/extractors/index"] == 1
        assert len(hub_request_counter) == 1

    def test_get_plugins_of_type(
        self,
        project: Project,
        hub_request_counter: Counter,
    ) -> None:
        extractors = project.hub_service.get_plugins_of_type(PluginType.EXTRACTORS)
        assert len(extractors) == 9
        assert len(extractors["tap-mock"].variants) == 2
        assert extractors["tap-mock"].variant_labels == [
            "meltano (default)",
            "singer-io",
        ]
        assert hub_request_counter["/extractors/index"] == 1

    def test_hub_auth(self, project) -> None:
        project.settings.set("hub_url_auth", "Bearer s3cr3t")
        assert project.hub_service.session.headers["Authorization"] == "Bearer s3cr3t"

    def test_server_error(self, project: Project) -> None:
        with pytest.raises(
            HubConnectionError,
            match=r"Could not connect to Meltano Hub. 500 Server Error",
        ) as exc_info:
            project.hub_service.find_definition(
                PluginType.EXTRACTORS,
                "this-returns-500",
            )

        assert isinstance(exc_info.value.__cause__, HTTPError)
        assert isinstance(exc_info.value.__cause__.response, Response)
        assert exc_info.value.__cause__.response.status_code == 500
        assert exc_info.value.__cause__.response.json() == {"error": "Server error"}
        assert exc_info.value.__cause__.response.url == (
            "https://hub.meltano.com/meltano/api/v1/plugins/extractors"
            "/this-returns-500--original"
        )

    def test_request_headers(self, project: Project) -> None:
        with mock.patch("click.get_current_context") as get_context:
            get_context.return_value = click.Context(
                hub,
                info_name="hub",
                parent=click.Context(cli, info_name="meltano"),
            )
            request = project.hub_service._build_request("GET", "https://example.com")
            assert request.headers["X-Meltano-Command"] == "meltano hub"

        with mock.patch("click.get_current_context") as get_context:
            get_context.return_value = None
            request = project.hub_service._build_request("GET", "https://example.com")
            assert "X-Meltano-Command" not in request.headers

    def test_custom_ca(self, project, monkeypatch) -> None:
        send_kwargs = {}

        class _Adapter(BaseAdapter):
            def send(
                self,
                request,  # noqa: ARG002
                **kwargs,
            ):
                nonlocal send_kwargs
                send_kwargs = kwargs

                response = Response()
                response._content = b'{"name": "tap-mock", "namespace": "tap_mock"}'
                response.status_code = 200
                return response

        mock_url = "hub://meltano"
        hub = project.hub_service
        hub.session.mount(mock_url, _Adapter())

        monkeypatch.setenv("REQUESTS_CA_BUNDLE", "/path/to/ca.pem")
        hub._get(mock_url)
        assert send_kwargs["verify"] == "/path/to/ca.pem"

    def test_custom_proxy(self, project, monkeypatch) -> None:
        send_kwargs = {}

        class _Adapter(BaseAdapter):
            def send(
                self,
                request,  # noqa: ARG002
                **kwargs,
            ):
                nonlocal send_kwargs
                send_kwargs = kwargs

                response = Response()
                response._content = b'{"name": "tap-mock", "namespace": "tap_mock"}'
                response.status_code = 200
                return response

        mock_url = "hub://meltano"
        hub = project.hub_service
        hub.session.mount(mock_url, _Adapter())

        monkeypatch.setenv("HTTPS_PROXY", "https://www.example.com:3128/")
        hub._get(mock_url)
        assert send_kwargs["proxies"] == {"https": "https://www.example.com:3128/"}
