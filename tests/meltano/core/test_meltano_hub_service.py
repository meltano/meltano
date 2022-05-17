from __future__ import annotations

from http import HTTPStatus

import pytest
import responses

from meltano.core.plugin.base import PluginType
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin_discovery_service import MeltanoHubService
from meltano.core.project import Project


class TestMeltanoHubService:
    @pytest.fixture
    def subject(self, project: Project):
        return MeltanoHubService(project)

    @responses.activate
    def test_find_definition(self, subject: MeltanoHubService):
        responses.add(
            responses.GET,
            "https://hub.meltano.com/meltano/api/v1/plugins/extractors/tap-mock--meltano",
            json={
                "name": "tap-mock",
                "namespace": "tap_mock",
                "variant": "mashey",
                "pip_url": "tap-mock",
                "capabilities": ["catalog", "discover", "state"],
                "settings": [
                    {"name": "foo"},
                    {"name": "bar", "kind": "password"},
                ],
            },
            status=HTTPStatus.OK,
        )
        definition = subject.find_definition(
            PluginType.EXTRACTORS,
            "tap-mock",
            variant_name="meltano",
        )
        assert definition.name == "tap-mock"

    @responses.activate
    def test_definition_not_found(self, subject: MeltanoHubService):
        responses.add(
            responses.GET,
            "https://hub.meltano.com/meltano/api/v1/plugins/extractors/tap-not-found",
            json={"error": "not found"},
            status=HTTPStatus.NOT_FOUND,
        )
        with pytest.raises(PluginNotFoundError):
            subject.find_definition(PluginType.EXTRACTORS, "tap-not-found")
