import pytest
import yaml
import os
import shutil

from meltano.core.project_add_service import ProjectAddService
from meltano.core.plugin_discovery_service import PluginNotFoundError
from meltano.core.plugin import Plugin, PluginType


class TestProjectAddService:
    def test_default_init_should_not_fail(self, project):
        add_service = ProjectAddService(project)
        assert add_service

    def test_missing_plugin_exception(self, project):
        add_service = ProjectAddService(project)
        try:
            add_service.add(PluginType.EXTRACTORS, "tap-missing")
        except Exception as e:
            assert type(e) is PluginNotFoundError

    def test_add_extractor(self, project):
        add_service = ProjectAddService(project)
        added = add_service.add(PluginType.EXTRACTORS, "tap-first")

        meltano_yml = yaml.load(project.meltanofile.open())

        assert added.canonical() in meltano_yml[PluginType.EXTRACTORS]
