"""Test the lock CLI command."""

from __future__ import annotations

from unittest import mock

import pytest
from click.testing import CliRunner

from meltano.cli import cli
from meltano.core.hub import MeltanoHubService
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_lock_service import PluginLock
from meltano.core.project import Project


class TestLock:
    @pytest.fixture(autouse=True)
    def patch_hub(self, meltano_hub_service: MeltanoHubService):
        with mock.patch(
            "meltano.core.project_plugins_service.MeltanoHubService",
            return_value=meltano_hub_service,
        ):
            yield

    @pytest.mark.parametrize(
        "args",
        [
            ["lock"],
            ["lock", "--all", "tap-mock"],
        ],
        ids=["noop", "all-and-plugin-name"],
    )
    def test_lock_invalid_options(self, cli_runner: CliRunner, args: list[str]):
        result = cli_runner.invoke(cli, args)
        assert result.exit_code == 1

        exception_message = "Exactly one of --all or plugin name must be specified."
        assert exception_message == str(result.exception)

    def test_lockfile_exists(
        self,
        cli_runner: CliRunner,
        project: Project,
        tap: ProjectPlugin,
        target: ProjectPlugin,
    ):
        lockfiles = list(project.root_plugins_dir().glob("./*/*.lock"))
        assert len(lockfiles) == 2

        result = cli_runner.invoke(cli, ["lock", "--all"])
        assert result.exit_code == 0
        assert "Lockfile exists for extractor tap-mock" in result.output
        assert "Lockfile exists for loader target-mock" in result.output
        assert "Locked definition" not in result.output

    def test_lockfile_update(
        self,
        cli_runner: CliRunner,
        project: Project,
        tap: ProjectPlugin,
        hub_endpoints: MeltanoHubService,
    ):
        tap_lock = PluginLock(project, tap)

        assert tap_lock.path.exists()
        old_checksum = tap_lock.sha256_checksum
        old_definition = tap_lock.load()

        # Update the plugin in Hub
        hub_endpoints["/extractors/tap-mock--meltano"]["settings"].append(
            {
                "name": "foo",
                "value": "bar",
            }
        )

        result = cli_runner.invoke(cli, ["lock", "--all", "--update"])
        assert result.exit_code == 0
        assert result.output.count("Lockfile exists") == 0
        assert result.output.count("Locked definition") == 2

        new_checksum = tap_lock.sha256_checksum
        new_definition = tap_lock.load()
        assert new_checksum != old_checksum
        assert len(new_definition.settings) == len(old_definition.settings) + 1

        new_setting = new_definition.settings[-1]
        assert new_setting.name == "foo"
        assert new_setting.value == "bar"

    def test_lockfile_update_extractors(
        self,
        cli_runner: CliRunner,
        project: Project,
        tap: ProjectPlugin,
        alternative_tap: ProjectPlugin,
        hub_endpoints: MeltanoHubService,
    ):
        lockfiles = list(project.root_plugins_dir().glob("./*/*.lock"))
        # 2 taps, 1 target
        assert len(lockfiles) == 3

        result = cli_runner.invoke(
            cli,
            ["lock", "--all", "--update", "--plugin-type", "extractor"],
        )
        assert result.exit_code == 0
        assert "Lockfile exists" not in result.output
        assert "Locked definition for extractor tap-mock" in result.output
        assert "Locked definition for extractor tap-mock--singer-io" in result.output
