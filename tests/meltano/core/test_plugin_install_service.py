from __future__ import annotations

import pytest
import yaml

from meltano.core.plugin_install_service import (
    PluginInstallReason,
    PluginInstallService,
)


class TestPluginInstallService:
    @pytest.fixture
    def subject(self, project):
        with open(project.meltanofile, "w") as file:
            file.write(
                yaml.dump(
                    {
                        "plugins": {
                            "extractors": [
                                {
                                    "name": "tap-gitlab",
                                    "pip_url": "git+https://gitlab.com/meltano/tap-gitlab.git",
                                },
                                {
                                    "name": "tap-gitlab--child-1",
                                    "inherit_from": "tap-gitlab",
                                },
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

        return PluginInstallService(project)

    def test_default_init_should_not_fail(self, subject):
        assert subject

    def test_remove_duplicates(self, subject):
        states, deduped_plugins = subject.remove_duplicates(
            plugins=subject.plugins_service.plugins(),
            reason=PluginInstallReason.INSTALL,
        )

        assert len(states) == 1
        assert states[0].plugin.name == "tap-gitlab--child-1" and states[0].skipped

        assert len(deduped_plugins) == 2
        assert [plugin.name for plugin in deduped_plugins] == [
            "tap-gitlab",
            "target-csv",
        ]

    @pytest.mark.slow
    def test_install_all(self, subject):
        all_plugins = subject.install_all_plugins()
        assert len(all_plugins) == 3

        assert all_plugins[2].plugin.name == "target-csv" and all_plugins[2].successful

        # test inherited plugins behaviors
        assert (
            all_plugins[0].plugin.name == "tap-gitlab--child-1"
            and all_plugins[0].successful
            and all_plugins[0].skipped
        )
        assert (
            all_plugins[1].plugin.name == "tap-gitlab"
            and all_plugins[1].successful
            and not all_plugins[1].skipped
        )
        assert all_plugins[0].plugin.venv_name == all_plugins[1].plugin.venv_name
        assert all_plugins[0].plugin.executable == all_plugins[1].plugin.executable
