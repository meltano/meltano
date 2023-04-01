from __future__ import annotations

import pytest
import yaml

from meltano.core.plugin_install_service import (
    PluginInstallReason,
    PluginInstallService,
)


class TestPluginInstallService:
    @pytest.fixture(
        params=({}, {"parallelism": -1}, {"parallelism": 2}),
        ids=("default", "-p=-1", "-p=2"),
    )
    def subject(self, project, request):
        with open(project.meltanofile, "w") as file:
            file.write(
                yaml.dump(
                    {
                        "plugins": {
                            "extractors": [
                                {
                                    "name": "tap-gitlab",
                                    "pip_url": "git+https://gitlab.com/meltano/tap-gitlab.git",  # noqa: E501
                                },
                                {
                                    "name": "tap-gitlab--child-1",
                                    "inherit_from": "tap-gitlab",
                                },
                            ],
                            "loaders": [
                                {
                                    "name": "target-csv",
                                    "pip_url": "git+https://gitlab.com/meltano/target-csv.git",  # noqa: E501
                                },
                            ],
                        },
                    },
                ),
            )
        project.refresh()
        return PluginInstallService(project, **request.param)

    def test_default_init_should_not_fail(self, subject):
        assert subject

    def test_remove_duplicates(self, subject):
        states, deduped_plugins = subject.remove_duplicates(
            plugins=subject.project.plugins.plugins(),
            reason=PluginInstallReason.INSTALL,
        )

        assert len(states) == 1
        assert states[0].plugin.name == "tap-gitlab--child-1"
        assert states[0].skipped

        assert len(deduped_plugins) == 2
        assert [plugin.name for plugin in deduped_plugins] == [
            "tap-gitlab",
            "target-csv",
        ]

    @pytest.mark.slow()
    def test_install_all(self, subject):
        all_plugins = subject.install_all_plugins()
        assert len(all_plugins) == 3

        assert all_plugins[2].plugin.name == "target-csv"
        assert all_plugins[2].successful

        # test inherited plugins behaviors
        assert all_plugins[0].plugin.name == "tap-gitlab--child-1"
        assert all_plugins[0].successful
        assert all_plugins[0].skipped

        assert all_plugins[1].plugin.name == "tap-gitlab"
        assert all_plugins[1].successful
        assert not all_plugins[1].skipped

        assert all_plugins[0].plugin.venv_name == all_plugins[1].plugin.venv_name
        assert all_plugins[0].plugin.executable == all_plugins[1].plugin.executable
