from __future__ import annotations

import pytest
import responses

from meltano.core.hub import MeltanoHubService
from meltano.core.hub.client import HubPluginVariantNotFound
from meltano.core.plugin.base import PluginType
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.project import Project


class TestMeltanoHubService:
    @pytest.fixture
    def subject(self, project: Project):
        return MeltanoHubService(project)

    def test_find_definition_specified_variant(
        self,
        subject: MeltanoHubService,
        requests_mock: responses.RequestsMock,
        hub_extractors_url: str,
        hub_tap_mock_url: str,
    ):
        definition = subject.find_definition(
            PluginType.EXTRACTORS,
            "tap-mock",
            variant_name="meltano",
        )
        assert requests_mock.assert_call_count(hub_extractors_url, 1)
        assert requests_mock.assert_call_count(hub_tap_mock_url, 1)
        assert definition.name == "tap-mock"
        assert definition.variants[0].name == "meltano"

    def test_find_definition_default_variant(
        self,
        subject: MeltanoHubService,
        requests_mock: responses.RequestsMock,
        hub_extractors_url: str,
        hub_tap_mock_url: str,
    ):
        definition = subject.find_definition(PluginType.EXTRACTORS, "tap-mock")
        assert requests_mock.assert_call_count(hub_extractors_url, 1)
        assert requests_mock.assert_call_count(hub_tap_mock_url, 1)
        assert definition.name == "tap-mock"
        assert definition.variants[0].name == "meltano"

    def test_definition_not_found(
        self,
        subject: MeltanoHubService,
        requests_mock: responses.RequestsMock,
        hub_extractors_url: str,
    ):
        plugin_url = subject.plugin_endpoint(PluginType.EXTRACTORS, "tap-not-found")

        with pytest.raises(PluginNotFoundError):
            subject.find_definition(PluginType.EXTRACTORS, "tap-not-found")

        assert requests_mock.assert_call_count(hub_extractors_url, 1)
        assert requests_mock.assert_call_count(plugin_url, 0)

    def test_variant_not_found(
        self,
        subject: MeltanoHubService,
        requests_mock: responses.RequestsMock,
        hub_extractors_url: str,
    ):
        plugin_url = subject.plugin_endpoint(
            PluginType.EXTRACTORS,
            "tap-mock",
            "not-found",
        )

        with pytest.raises(HubPluginVariantNotFound):
            subject.find_definition(PluginType.EXTRACTORS, "tap-mock", "not-found")

        assert requests_mock.assert_call_count(hub_extractors_url, 1)
        assert requests_mock.assert_call_count(plugin_url, 0)

    def test_get_plugins_of_type(
        self,
        subject: MeltanoHubService,
        requests_mock: responses.RequestsMock,
        hub_extractors_url: str,
    ):
        extractors = subject.get_plugins_of_type(PluginType.EXTRACTORS)
        assert requests_mock.assert_call_count(hub_extractors_url, 1)
        assert len(extractors) == 2
        assert len(extractors["tap-mock"].variants) == 2
        assert extractors["tap-mock"].variant_labels == [
            "meltano (default)",
            "singer-io",
        ]
