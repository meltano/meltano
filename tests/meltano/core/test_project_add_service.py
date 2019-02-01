import pytest
import yaml
import os
import shutil

from meltano.core.project_add_service import ProjectAddService
from meltano.core.plugin_discovery_service import PluginNotFoundError
from meltano.core.plugin import PluginType


class TestProjectAddService:
    @pytest.fixture
    def subject(self, project_add_service):
        return project_add_service

    def test_missing_plugin_exception(self, subject):
        try:
            subject.add(PluginType.EXTRACTORS, "tap-missing")
        except Exception as e:
            assert type(e) is PluginNotFoundError

    @pytest.mark.parametrize(
        ("plugin_type", "plugin_name"),
        [
            (PluginType.EXTRACTORS, "tap-mock"),
            (PluginType.LOADERS, "target-mock"),
            (PluginType.TRANSFORMERS, "transformer-mock"),
            (PluginType.TRANSFORMS, "tap-mock-transform"),
        ],
    )
    def test_add(self, plugin_type, plugin_name, subject, project):
        added = subject.add(plugin_type, plugin_name)
        assert added.canonical() in project.meltano["plugins"][plugin_type]
