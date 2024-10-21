from __future__ import annotations

import typing as t
from unittest.mock import AsyncMock, patch

import pytest
import yaml

from meltano.core.plugin import PluginType
from meltano.core.plugin_install_service import (
    PluginInstallReason,
    PluginInstallService,
    get_pip_install_args,
)
from meltano.core.project_plugins_service import PluginAlreadyAddedException

if t.TYPE_CHECKING:
    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project


class TestPluginInstallService:
    @pytest.fixture(
        params=({}, {"parallelism": -1}, {"parallelism": 2}),
        ids=("default", "-p=-1", "-p=2"),
    )
    def subject(self, project: Project, request):
        with project.meltanofile.open("w") as file:
            file.write(
                yaml.dump(
                    {
                        "plugins": {
                            "extractors": [
                                {
                                    "name": "tap-gitlab",
                                    "namespace": "tap_gitlab",
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
                                    "namespace": "target_csv",
                                    "pip_url": "git+https://gitlab.com/meltano/target-csv.git",
                                },
                            ],
                        },
                    },
                ),
            )
        project.refresh()
        return PluginInstallService(project, **request.param)

    @pytest.fixture
    def tap(self, project_add_service):
        try:
            return project_add_service.add(
                PluginType.EXTRACTORS,
                "tap-mock",
                variant="meltano",
            )
        except PluginAlreadyAddedException as err:  # pragma: no cover
            return err.plugin

    @pytest.fixture
    def inherited_tap(self, project_add_service, tap):
        try:
            return project_add_service.add(
                PluginType.EXTRACTORS,
                "tap-mock-inherited",
                inherit_from=tap.name,
            )
        except PluginAlreadyAddedException as err:  # pragma: no cover
            return err.plugin

    @pytest.fixture
    def inherited_inherited_tap(self, project_add_service, inherited_tap):
        try:
            return project_add_service.add(
                PluginType.EXTRACTORS,
                "tap-mock-inherited-inherited",
                inherit_from=inherited_tap.name,
            )
        except PluginAlreadyAddedException as err:  # pragma: no cover
            return err.plugin

    @pytest.fixture
    def mapper(self, project_add_service):
        try:
            return project_add_service.add(
                PluginType.MAPPERS,
                "mapper-mock",
                variant="meltano",
                mappings=[
                    {
                        "name": "mock-mapping-0",
                        "config": {
                            "transformations": [
                                {
                                    "field_id": "author_email",
                                    "tap_stream_name": "commits",
                                    "type": "MASK-HIDDEN",
                                },
                            ],
                        },
                    },
                    {
                        "name": "mock-mapping-1",
                        "config": {
                            "transformations": [
                                {
                                    "field_id": "given_name",
                                    "tap_stream_name": "users",
                                    "type": "lowercase",
                                },
                            ],
                        },
                    },
                ],
            )
        except PluginAlreadyAddedException as err:  # pragma: no cover
            return err.plugin

    @pytest.fixture
    def mapping(self, project: Project, mapper: ProjectPlugin):
        name: str = mapper.extra_config["_mappings"][0]["name"]
        return project.plugins.find_plugin(name)

    def test_default_init_should_not_fail(self, subject) -> None:
        assert subject

    def test_remove_duplicates(self, subject) -> None:
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

    @pytest.mark.slow
    async def test_install_all(self, subject) -> None:
        all_plugins = await subject.install_all_plugins()
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

        assert (
            all_plugins[0].plugin.plugin_dir_name
            == all_plugins[1].plugin.plugin_dir_name
        )
        assert all_plugins[0].plugin.executable == all_plugins[1].plugin.executable

    def test_get_quoted_pip_install_args(self, project) -> None:
        with project.meltanofile.open("w") as file:
            file.write(
                yaml.dump(
                    {
                        "plugins": {
                            "extractors": [
                                {
                                    "name": "tap-gitlab",
                                    "namespace": "tap_gitlab",
                                    "pip_url": "'tap-gitlab @ git+https://gitlab.com/meltano/tap-gitlab.git' python-json-logger",  # noqa: E501
                                },
                            ],
                        },
                    },
                ),
            )
        project.refresh()
        plugin = next(project.plugins.plugins())
        assert get_pip_install_args(project, plugin) == [
            "tap-gitlab @ git+https://gitlab.com/meltano/tap-gitlab.git",
            "python-json-logger",
        ]

    @patch("meltano.core.venv_service.VenvService.install_pip_args", AsyncMock())
    @pytest.mark.usefixtures("reset_project_context")
    async def test_auto_install(
        self,
        subject: PluginInstallService,
        tap,
        inherited_tap,
        inherited_inherited_tap,
    ) -> None:
        plugin = tap
        inherited_plugin = inherited_tap
        inherited_inherited_plugin = inherited_inherited_tap

        state = await subject.install_plugin_async(
            plugin,
            reason=PluginInstallReason.AUTO,
        )

        assert not state.skipped, "Expected plugin with no venv to be installed"

        state = await subject.install_plugin_async(
            plugin,
            reason=PluginInstallReason.AUTO,
        )

        assert (
            state.skipped
        ), "Expected plugin with venv and matching fingerprint to not be installed"

        state = await subject.install_plugin_async(
            inherited_plugin,
            reason=PluginInstallReason.AUTO,
        )

        assert state.skipped, (
            "Expected plugin inheriting from another plugin with venv and matching"
            " fingerprint to not be installed"
        )

        state = await subject.install_plugin_async(
            inherited_inherited_plugin,
            reason=PluginInstallReason.AUTO,
        )

        assert state.skipped, (
            "Expected plugin inheriting from another inherited plugin with venv and"
            " matching fingerprint to not be installed"
        )

        plugin.pip_url = "changed"
        state = await subject.install_plugin_async(
            plugin,
            reason=PluginInstallReason.AUTO,
        )

        assert (
            not state.skipped
        ), "Expected plugin with venv and non-matching fingerprint to be installed"

        plugin.pip_url = "$MISSING_ENV_VAR"
        state = await subject.install_plugin_async(
            plugin,
            reason=PluginInstallReason.AUTO,
        )

        assert (
            state.skipped
        ), "Expected plugin with missing env var in pip URL to not be installed"

    @patch("meltano.core.venv_service.VenvService.install_pip_args", AsyncMock())
    @pytest.mark.usefixtures("reset_project_context")
    async def test_auto_install_mapper_by_mapping(
        self,
        subject: PluginInstallService,
        mapper,
        mapping,
    ) -> None:
        state = await subject.install_plugin_async(
            mapping,
            reason=PluginInstallReason.AUTO,
        )

        assert not state.skipped, "Expected mapper defining mapping to be installed"

        state = await subject.install_plugin_async(
            mapper,
            reason=PluginInstallReason.AUTO,
        )

        assert state.skipped, "Expected mapper to not be installed"

        state = await subject.install_plugin_async(
            mapping,
            reason=PluginInstallReason.AUTO,
        )

        assert state.skipped, "Expected mapper defining mapping to not be installed"
