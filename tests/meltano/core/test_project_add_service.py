import pytest
import yaml
import os
import shutil

from meltano.core.project_add_service import ProjectAddService, MissingPluginException


class TestProjectAddService:
    def test_default_init_should_not_fail(self):
        add_service = ProjectAddService()
        assert add_service

    def test_missing_plugin_exception(self):
        add_service = ProjectAddService()
        try:
            add_service.add()
        except Exception as e:
            assert type(e) is MissingPluginException

    def test_add_extractor(self):
        add_service = ProjectAddService("extractors", "first")
        add_service.add()

        meltano_yml = yaml.load(open("./meltano.yml").read())
        os.remove("./meltano.yml")
        assert meltano_yml == {
            "extractors": [
                {"name": "first", "url": "git+https://gitlab.com/meltano/tap-first.git"}
            ]
        }
