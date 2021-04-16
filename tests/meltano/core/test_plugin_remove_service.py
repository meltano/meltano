import pytest
import yaml
from meltano.core.plugin_remove_service import PluginRemoveService


class TestPluginRemoveService:
    @pytest.fixture
    def subject(self, project):
        with open(project.meltanofile, "w") as meltano_yml:
            meltano_yml.write(
                yaml.dump(
                    {
                        "plugins": {
                            "extractors": [
                                {
                                    "name": "tap-gitlab",
                                    "pip_url": "git+https://gitlab.com/meltano/tap-gitlab.git",
                                }
                            ],
                            "loaders": [
                                {
                                    "name": "target-csv",
                                    "pip_url": "git+https://gitlab.com/meltano/target-csv.git",
                                }
                            ],
                        }
                    }
                )
            )

        return PluginRemoveService(project)

    def test_default_init_should_not_fail(self, subject):
        assert subject

    def test_remove(self, subject):
        discovered_plugins = subject.plugins_service.plugins()
        removed_plugins, total_plugins = subject.remove_plugins(
            list(discovered_plugins)
        )

        assert removed_plugins == total_plugins
