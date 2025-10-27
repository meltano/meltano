"""Test the lock CLI command."""

from __future__ import annotations

import typing as t

import pytest

from meltano.cli import cli
from meltano.cli.utils import CliError
from meltano.core.plugin_lock_service import PluginLockService

if t.TYPE_CHECKING:
    from click.testing import CliRunner

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

        result = cli_runner.invoke(
            cli,
            [
                "--log-level=debug",
                "--log-format=uncolored",
                "lock",
            ],
        )
        assert result.exit_code == 0
        assert "Lockfile exists for extractor tap-mock" in result.stderr
        assert "Lockfile exists for loader target-mock" in result.stderr
        assert "Locked definition" not in result.stderr

    @pytest.mark.order(2)
    def test_lockfile_update(
        self,
        cli_runner: CliRunner,
        project: Project,
        tap: ProjectPlugin,
        hub_endpoints: dict[str, dict],
    ) -> None:
        subject = PluginLockService(project)
        tap_lock_path = subject.plugin_lock_path(plugin=tap, variant_name=tap.variant)

        assert tap_lock_path.exists()
        old_definition = subject.load_definition(
            plugin_type=tap.type,
            plugin_name=tap.name,
            variant_name=tap.variant,
        )
        old_variant = old_definition.find_variant(tap.variant)

        # Update the plugin in Hub
        hub_endpoints["/extractors/tap-mock--meltano"]["settings"].append(
            {
                "name": "foo",
                "value": "bar",
            },
        )

        result = cli_runner.invoke(
            cli,
            [
                "--log-level=debug",
                "--log-format=uncolored",
                "lock",
                "--update",
            ],
        )
        assert result.exit_code == 0
        assert result.stderr.count("Lockfile exists") == 0
        assert result.stderr.count("Locked definition") == 2
        new_definition = subject.load_definition(
            plugin_type=tap.type,
            plugin_name=tap.name,
            variant_name=tap.variant,
        )
        new_variant = new_definition.find_variant(tap.variant)
        assert len(new_variant.settings) == len(old_variant.settings) + 1

        new_setting = new_variant.settings[-1]
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
            [
                "--log-level=debug",
                "--log-format=uncolored",
                "lock",
                "--update",
                "--plugin-type",
                "extractor",
            ],
        )
        assert result.exit_code == 0
        assert "Lockfile exists" not in result.stderr
        assert "Locked definition for extractor tap-mock" in result.stderr
        assert "Extractor tap-mock-inherited is an inherited plugin" in result.stderr

    def test_lock_plugin_not_found(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(cli, ["lock", "not-a-plugin"])
        assert result.exit_code == 1
        assert isinstance(result.exception, CliError)
        assert "No matching plugin(s) found" in str(result.exception)
