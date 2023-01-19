from __future__ import annotations

from collections import Counter

import click
import mock
import pytest
from requests import HTTPError, Response

from meltano.cli import cli
from meltano.cli.discovery import discover
from meltano.core.hub import MeltanoHubService
from meltano.core.hub.client import HubConnectionError, HubPluginVariantNotFoundError
from meltano.core.plugin.base import PluginType, Variant
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.project_settings_service import ProjectSettingsService


class TestMeltanoHubService:
    @pytest.fixture
    def subject(self, meltano_hub_service: MeltanoHubService):
        return meltano_hub_service

    def test_find_definition_specified_variant(
        self,
        subject: MeltanoHubService,
        hub_request_counter: Counter,
    ):
        definition = subject.find_definition(
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
        subject: MeltanoHubService,
        hub_request_counter: Counter,
    ):
        definition = subject.find_definition(PluginType.EXTRACTORS, "tap-mock")
        assert definition.name == "tap-mock"
        assert definition.variants[0].name == "meltano"

        assert hub_request_counter["/extractors/index"] == 1
        assert hub_request_counter["/extractors/tap-mock--meltano"] == 1

    def test_find_definition_original_variant(
        self,
        subject: MeltanoHubService,
        hub_request_counter: Counter,
    ):
        definition = subject.find_definition(
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
        subject: MeltanoHubService,
        hub_request_counter: Counter,
    ):
        with pytest.raises(PluginNotFoundError):
            subject.find_definition(PluginType.EXTRACTORS, "tap-not-found")

        assert hub_request_counter["/extractors/index"] == 1
        assert len(hub_request_counter) == 1

    def test_variant_not_found(
        self,
        subject: MeltanoHubService,
        hub_request_counter: Counter,
    ):
        with pytest.raises(HubPluginVariantNotFoundError):
            subject.find_definition(PluginType.EXTRACTORS, "tap-mock", "not-found")

        assert hub_request_counter["/extractors/index"] == 1
        assert len(hub_request_counter) == 1

    def test_get_plugins_of_type(
        self,
        subject: MeltanoHubService,
        hub_request_counter: Counter,
    ):
        extractors = subject.get_plugins_of_type(PluginType.EXTRACTORS)
        assert len(extractors) == 35  # noqa: WPS432
        assert len(extractors["tap-mock"].variants) == 2
        assert extractors["tap-mock"].variant_labels == [
            "meltano (default)",
            "singer-io",
        ]
        assert hub_request_counter["/extractors/index"] == 1

    def test_hub_auth(self, project):
        ProjectSettingsService(project).set("hub_url_auth", "Bearer s3cr3t")
        hub = MeltanoHubService(project)
        assert hub.session.headers["Authorization"] == "Bearer s3cr3t"

    def test_server_error(self, subject: MeltanoHubService):
        with pytest.raises(
            HubConnectionError,
            match="Could not connect to Meltano Hub. 500 Server Error",
        ) as exc_info:
            subject.find_definition(PluginType.EXTRACTORS, "this-returns-500")

        assert isinstance(exc_info.value.__cause__, HTTPError)
        assert isinstance(exc_info.value.__cause__.response, Response)
        assert exc_info.value.__cause__.response.status_code == 500
        assert exc_info.value.__cause__.response.json() == {"error": "Server error"}
        assert exc_info.value.__cause__.response.url == (
            "https://hub.meltano.com/meltano/api/v1/plugins/extractors"
            "/this-returns-500--original"
        )

    def test_request_headers(self, subject: MeltanoHubService):
        with mock.patch("click.get_current_context") as get_context:
            get_context.return_value = click.Context(
                discover,
                info_name="discover",
                parent=click.Context(cli, info_name="meltano"),
            )
            request = subject._build_request("GET", "https://example.com")
            assert request.headers["X-Meltano-Command"] == "meltano discover"

        with mock.patch("click.get_current_context") as get_context:
            get_context.return_value = None
            request = subject._build_request("GET", "https://example.com")
            assert "X-Meltano-Command" not in request.headers
