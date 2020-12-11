import os
import shutil

import pytest
import yaml
from meltano.core.plugin import PluginType
from meltano.core.plugin_discovery_service import PluginNotFoundError
from meltano.core.project_add_service import ProjectAddService


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

        assert added in project.meltano["plugins"][plugin_type]
