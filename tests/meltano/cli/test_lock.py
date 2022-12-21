"""Test the lock CLI command."""

from __future__ import annotations

import mock
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

    @pytest.mark.order(0)
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

    @pytest.mark.order(1)
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
        assert "Lockfile exists for extractor tap-mock" in result.stdout
        assert "Lockfile exists for loader target-mock" in result.stdout
        assert "Locked definition" not in result.stdout

    @pytest.mark.order(2)
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
        assert result.stdout.count("Lockfile exists") == 0
        assert result.stdout.count("Locked definition") == 2

        new_checksum = tap_lock.sha256_checksum
        new_definition = tap_lock.load()
        assert new_checksum != old_checksum
        assert len(new_definition.settings) == len(old_definition.settings) + 1

        new_setting = new_definition.settings[-1]
        assert new_setting.name == "foo"
        assert new_setting.value == "bar"

    @pytest.mark.order(3)
    def test_lockfile_update_extractors(
        self,
        cli_runner: CliRunner,
        project: Project,
        tap: ProjectPlugin,
        inherited_tap: ProjectPlugin,
        hub_endpoints: MeltanoHubService,
    ):
        lockfiles = list(project.root_plugins_dir().glob("./*/*.lock"))
        # 1 tap, 1 target
        assert len(lockfiles) == 2

        result = cli_runner.invoke(
            cli,
            ["lock", "--all", "--update", "--plugin-type", "extractor"],
        )
        assert result.exit_code == 0
        assert "Lockfile exists" not in result.stdout
        assert "Locked definition for extractor tap-mock" in result.stdout
        assert "Extractor tap-mock-inherited is an inherited plugin" in result.stdout
