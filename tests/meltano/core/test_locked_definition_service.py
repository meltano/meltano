from __future__ import annotations

import json

import pytest

from meltano.core.plugin import PluginType
from meltano.core.plugin.base import StandalonePlugin
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin_discovery_service import LockedDefinitionService

HTTP_STATUS_TEAPOT = 418


@pytest.fixture
def subject(project):
    yield LockedDefinitionService(project)


class TestLockedDefinitionService:
    @pytest.fixture
    def locked_plugin(self, subject: LockedDefinitionService):
        """Locked plugin definition.

        Yields:
            StandalonePlugin: A locked plugin.
        """
        definition = StandalonePlugin(
            PluginType.EXTRACTORS,
            "tap-locked",
            "tap_locked",
            variant="meltano",
            foo="bar",
        )
        path = subject.project.plugin_lock_path(
            definition.plugin_type,
            definition.name,
            definition.variant,
        )
        with path.open("w") as file:
            json.dump(definition.canonical(), file)
        yield definition

        path.unlink()

    def test_definition(
        self,
        subject: LockedDefinitionService,
        locked_plugin: StandalonePlugin,
    ):
        with pytest.raises(PluginNotFoundError):
            subject.find_definition(PluginType.EXTRACTORS, "unknown")

        plugin_def = subject.find_definition(
            PluginType.EXTRACTORS,
            "tap-locked",
            variant_name="meltano",
        )
        assert plugin_def.type == PluginType.EXTRACTORS
        assert plugin_def.name == "tap-locked"
        assert plugin_def.namespace == "tap_locked"
        assert plugin_def.extras["foo"] == "bar"
        assert len(plugin_def.variants) == 1

    def test_find_base_plugin(
        self,
        subject: LockedDefinitionService,
        locked_plugin: StandalonePlugin,
    ):
        base_plugin = subject.find_base_plugin(
            PluginType.EXTRACTORS,
            "tap-locked",
            variant="meltano",
        )
        assert base_plugin.type == PluginType.EXTRACTORS
        assert base_plugin.name == "tap-locked"
        assert base_plugin._variant == base_plugin.variants[0]
        assert base_plugin.variant == base_plugin.variants[0].name
