import pytest
import yaml
import os
import shutil

from meltano.core.project_add_service import ProjectAddService, MissingPluginException


class TestProjectAddService:
    def test_default_init_should_not_fail(self, project):
        add_service = ProjectAddService(project)
        assert add_service

    def test_missing_plugin_exception(self, project):
        add_service = ProjectAddService(project)
        try:
            add_service.add()
        except Exception as e:
            assert type(e) is MissingPluginException

    def test_add_extractor(self, project):
        add_service = ProjectAddService(project, "extractors", "tap-first")
        add_service.add()

        meltano_yml = yaml.load(project.meltanofile.open())
        os.remove(project.meltanofile.resolve())

        assert meltano_yml == {
            "extractors": [
                {"name": "tap-first", "url": "git+https://gitlab.com/meltano/tap-first.git"}
            ]
        }
