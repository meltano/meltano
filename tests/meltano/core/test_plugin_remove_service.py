import os

import pytest
import yaml
from meltano.core.plugin_remove_service import PluginRemoveService


class TestPluginRemoveService:
    @pytest.fixture
    def subject(self, project):
        return PluginRemoveService(project)

    @pytest.fixture
    def add(self, subject: PluginRemoveService):
        with open(subject.project.meltanofile, "w") as meltano_yml:
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

    @pytest.fixture
    def install(self, subject: PluginRemoveService):
        tap_gitlab_installation = subject.project.meltano_dir().joinpath(
            "extractors", "tap-gitlab"
        )
        target_csv_installation = subject.project.meltano_dir().joinpath(
            "loaders", "target-csv"
        )

        os.makedirs(tap_gitlab_installation)
        os.makedirs(target_csv_installation)

    def test_default_init_should_not_fail(self, subject):
        assert subject

    def test_remove(
        self,
        subject: PluginRemoveService,
        add,
        install,
    ):
        plugins = list(subject.plugins_service.plugins())
        removed_plugins, total_plugins = subject.remove_plugins(plugins)

        assert removed_plugins == total_plugins

        for plugin in plugins:
            # check removed from meltano.yml
            with open(subject.project.meltanofile) as meltanofile:
                meltano_yml = yaml.safe_load(meltanofile)

                with pytest.raises(KeyError):
                    plugin_data = meltano_yml[plugin.type, plugin.name]
                    assert not plugin_data

            # check removed installation
            assert not os.path.exists(
                subject.project.meltano_dir().joinpath(plugin.type, plugin.name)
            )
