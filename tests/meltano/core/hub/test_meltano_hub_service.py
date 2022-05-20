from __future__ import annotations

import pytest
import responses

from meltano.core.hub import MeltanoHubService
from meltano.core.plugin.base import PluginType
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.project import Project


class TestMeltanoHubService:
    @pytest.fixture
    def subject(self, project: Project):
        return MeltanoHubService(project)

    @responses.activate
    def test_find_definition(self, subject: MeltanoHubService, get_hub_response):
        url = subject.plugin_endpoint(PluginType.EXTRACTORS, "tap-mock", "meltano")
        responses.add_callback(responses.GET, url, callback=get_hub_response)
        definition = subject.find_definition(
            PluginType.EXTRACTORS,
            "tap-mock",
            variant_name="meltano",
        )
        assert responses.assert_call_count(url, 1)
        assert definition.name == "tap-mock"
        assert definition.variants[0].name == "meltano"

    @responses.activate
    def test_definition_not_found(self, subject: MeltanoHubService, get_hub_response):
        plugin_url = subject.plugin_endpoint(PluginType.EXTRACTORS, "tap-not-found")
        responses.add_callback(responses.GET, plugin_url, callback=get_hub_response)

        with pytest.raises(PluginNotFoundError):
            subject.find_definition(PluginType.EXTRACTORS, "tap-not-found")

        assert responses.assert_call_count(plugin_url, 1)

    @responses.activate
    def test_get_plugins_of_type(self, subject: MeltanoHubService, get_hub_response):
        url = subject.plugin_type_endpoint(PluginType.EXTRACTORS)
        responses.add_callback(responses.GET, url, callback=get_hub_response)
        extractors = subject.get_plugins_of_type(PluginType.EXTRACTORS)
        assert responses.assert_call_count(url, 1)
        assert len(extractors) == 2
        assert len(extractors["tap-mock"].variants) == 2
        assert extractors["tap-mock"].variant_labels == [
            "meltano (default)",
            "singer-io",
        ]
