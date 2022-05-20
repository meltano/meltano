from __future__ import annotations

from http import HTTPStatus
from pathlib import Path
from typing import Any

import pytest
import responses
from requests import PreparedRequest

from meltano.core.plugin.base import PluginType
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin_discovery_service import MeltanoHubService
from meltano.core.project import Project


def get_response(request: PreparedRequest) -> Any:
    endpoint_mapping = {
        "/plugins/extractors/index": "extractors.json",
        "/plugins/loaders/index": "loaders.json",
        "/plugins/extractors/tap-mock--meltano": "tap-mock--meltano.json",
    }

    _, endpoint = request.path_url.split("/meltano/api/v1")

    try:
        filename = endpoint_mapping[endpoint]
    except KeyError:
        return (HTTPStatus.NOT_FOUND, {}, '{"error": "not found"}')

    base_path = Path(__file__).parent.parent.parent.joinpath("fixtures", "hub")
    file_path = base_path / filename
    return (HTTPStatus.OK, {"Content-Type": "application/json"}, file_path.read_text())


class TestMeltanoHubService:
    @pytest.fixture
    def subject(self, project: Project):
        return MeltanoHubService(project)

    @responses.activate
    def test_find_definition(self, subject: MeltanoHubService):
        responses.add_callback(
            responses.GET,
            subject.plugin_endpoint(PluginType.EXTRACTORS, "tap-mock", "meltano"),
            callback=get_response,
        )
        definition = subject.find_definition(
            PluginType.EXTRACTORS,
            "tap-mock",
            variant_name="meltano",
        )
        assert definition.name == "tap-mock"
        assert definition.variants[0].name == "meltano"

    @responses.activate
    def test_definition_not_found(self, subject: MeltanoHubService):
        responses.add_callback(
            responses.GET,
            subject.plugin_endpoint(PluginType.EXTRACTORS, "tap-not-found"),
            callback=get_response,
        )
        with pytest.raises(PluginNotFoundError):
            subject.find_definition(PluginType.EXTRACTORS, "tap-not-found")
