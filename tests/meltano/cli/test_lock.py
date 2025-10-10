"""Test the lock CLI command."""

from __future__ import annotations

import typing as t

import pytest

from meltano.cli import cli
from meltano.cli.utils import CliError
from meltano.core.plugin_lock_service import PluginLock

if t.TYPE_CHECKING:
    from click.testing import CliRunner

    from meltano.core.hub import MeltanoHubService
    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project


class TestLock:
    @pytest.mark.order(0)
    @pytest.mark.usefixtures("project")
    def test_lock_no_plugins(self, cli_runner: CliRunner) -> None:
        exception_message = "No matching plugin(s) found"

        result = cli_runner.invoke(cli, ["lock"])
        assert exception_message == str(result.exception)

        result = cli_runner.invoke(cli, ["lock", "--update"])
        assert exception_message == str(result.exception)

    @pytest.mark.order(1)
    @pytest.mark.usefixtures("tap", "target")
    def test_lockfile_exists(
        self,
        cli_runner: CliRunner,
        project: Project,
    ) -> None:
        lockfiles = list(project.root_plugins_dir().glob("./*/*.lock"))
        assert len(lockfiles) == 2

        result = cli_runner.invoke(cli, ["lock"])
        assert result.exit_code == 0
        # Verify lockfiles still exist and weren't modified
        assert len(list(project.root_plugins_dir().glob("./*/*.lock"))) == 2

    @pytest.mark.order(2)
    def test_lockfile_update(
        self,
        cli_runner: CliRunner,
        project: Project,
        tap: ProjectPlugin,
        hub_endpoints: MeltanoHubService,
    ) -> None:
        tap_lock = PluginLock(project, tap)

        assert tap_lock.path.exists()
        old_checksum = tap_lock.sha256_checksum
        old_definition = tap_lock.load()

        # Update the plugin in Hub
        hub_endpoints["/extractors/tap-mock--meltano"]["settings"].append(
            {
                "name": "foo",
                "value": "bar",
            },
        )

        result = cli_runner.invoke(cli, ["lock", "--update"])
        assert result.exit_code == 0

        new_checksum = tap_lock.sha256_checksum
        new_definition = tap_lock.load()
        assert new_checksum != old_checksum
        assert len(new_definition.settings) == len(old_definition.settings) + 1

        new_setting = new_definition.settings[-1]
        assert new_setting.name == "foo"
        assert new_setting.value == "bar"

    @pytest.mark.order(3)
    @pytest.mark.usefixtures("tap", "inherited_tap", "hub_endpoints")
    def test_lockfile_update_extractors(
        self,
        cli_runner: CliRunner,
        project: Project,
    ) -> None:
        lockfiles = list(project.root_plugins_dir().glob("./*/*.lock"))
        # 1 tap, 1 target
        assert len(lockfiles) == 2

        result = cli_runner.invoke(
            cli,
            ["lock", "--update", "--plugin-type", "extractor"],
        )
        assert result.exit_code == 0
        # Verify only extractor lockfiles were updated (not the loader)
        extractor_lockfiles = list(
            project.root_plugins_dir("extractors").glob("./*.lock")
        )
        assert len(extractor_lockfiles) == 1

    @pytest.mark.usefixtures("project")
    def test_lock_plugin_not_found(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(cli, ["lock", "not-a-plugin"])
        assert result.exit_code == 1
        assert isinstance(result.exception, CliError)
        assert "No matching plugin(s) found" in str(result.exception)
