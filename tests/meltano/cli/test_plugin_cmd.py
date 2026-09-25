from __future__ import annotations

import json
import typing as t

import pytest

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.cli.plugin import CUSTOM, INHERITED
from meltano.core.plugin import PluginType
from meltano.core.plugin_lock_service import PluginLockService, PluginUpdate

if t.TYPE_CHECKING:
    from click.testing import CliRunner, Result

    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project
    from meltano.core.project_add_service import ProjectAddService


def listed(result: Result) -> dict[str, dict[str, t.Any]]:
    """Parse JSON output into a mapping of plugin name to its record."""
    return {entry["name"]: entry for entry in json.loads(result.stdout)}


@pytest.fixture(scope="class")
def custom_tap(project_add_service: ProjectAddService) -> ProjectPlugin:
    """A plugin that carries its own definition, rather than one from the Hub."""
    return project_add_service.add(
        PluginType.EXTRACTORS,
        "tap-custom",
        namespace="tap_custom",
        pip_url="tap-custom",
        executable="tap-custom",
    )


class TestPluginListOrder:
    """A separate class, so no other test defines a plugin in this project."""

    def test_keeps_the_order_of_the_project_file(
        self,
        project: Project,  # noqa: ARG002
        project_add_service: ProjectAddService,
        cli_runner: CliRunner,
    ) -> None:
        # Names chosen so that the order of definition is not the order of
        # the names, and a loader defined first does not come out first.
        for plugin_type, name in (
            (PluginType.LOADERS, "target-zulu"),
            (PluginType.EXTRACTORS, "tap-zulu"),
            (PluginType.EXTRACTORS, "tap-alpha"),
        ):
            project_add_service.add(
                plugin_type,
                name,
                namespace=name.replace("-", "_"),
                pip_url=name,
                executable=name,
            )

        result = cli_runner.invoke(cli, ("plugin", "list", "--format", "json"))

        assert_cli_runner(result)
        names = [entry["name"] for entry in json.loads(result.stdout)]
        assert names == ["tap-zulu", "tap-alpha", "target-zulu"]


class TestPluginListWithoutPlugins:
    def test_reports_no_plugins_defined(
        self,
        project: Project,  # noqa: ARG002
        cli_runner: CliRunner,
    ) -> None:
        result = cli_runner.invoke(cli, ("plugin", "list"))

        assert_cli_runner(result)
        assert "No plugins are defined in this project." in result.stdout
        assert "meltano add" in result.stdout

    def test_json_is_empty(
        self,
        project: Project,  # noqa: ARG002
        cli_runner: CliRunner,
    ) -> None:
        result = cli_runner.invoke(cli, ("plugin", "list", "--format", "json"))

        assert_cli_runner(result)
        assert json.loads(result.stdout) == []


class TestPluginListDeclaredPlugins:
    def test_lists_declared_plugins(
        self,
        project: Project,  # noqa: ARG002
        tap: ProjectPlugin,
        target: ProjectPlugin,
        cli_runner: CliRunner,
    ) -> None:
        result = cli_runner.invoke(cli, ("plugin", "list", "--format", "json"))

        assert_cli_runner(result)
        entries = listed(result)
        assert entries[tap.name]["type"] == "extractor"
        assert entries[tap.name]["pip_url"] == tap.pip_url
        assert entries[target.name]["type"] == "loader"

    def test_inherited_plugin_resolves_through_its_parent(
        self,
        project: Project,  # noqa: ARG002
        tap: ProjectPlugin,
        inherited_tap: ProjectPlugin,
        cli_runner: CliRunner,
    ) -> None:
        result = cli_runner.invoke(cli, ("plugin", "list", "--format", "json"))

        assert_cli_runner(result)
        entries = listed(result)
        assert entries[inherited_tap.name]["inherit_from"] == tap.name
        # The variant is resolved through the parent, rather than declared.
        assert entries[inherited_tap.name]["variant"] == entries[tap.name]["variant"]

    def test_text_output_marks_an_inherited_variant(
        self,
        project: Project,  # noqa: ARG002
        tap: ProjectPlugin,
        inherited_tap: ProjectPlugin,  # noqa: ARG002
        cli_runner: CliRunner,
    ) -> None:
        result = cli_runner.invoke(cli, ("plugin", "list"))

        assert_cli_runner(result)
        # The parent is named in its own column, and the child declares no
        # variant of its own.
        assert "INHERIT FROM" in result.stdout
        assert tap.name in result.stdout
        assert INHERITED.replace("[dim]", "").replace("[/dim]", "") in result.stdout

    def test_text_output_lists_the_plugin(
        self,
        project: Project,  # noqa: ARG002
        tap: ProjectPlugin,
        cli_runner: CliRunner,
    ) -> None:
        result = cli_runner.invoke(cli, ("plugin", "list"))

        assert_cli_runner(result)
        assert tap.name in result.stdout
        assert "extractor" in result.stdout

    def test_custom_plugins_are_marked(
        self,
        project: Project,  # noqa: ARG002
        custom_tap: ProjectPlugin,
        tap: ProjectPlugin,
        cli_runner: CliRunner,
    ) -> None:
        result = cli_runner.invoke(cli, ("plugin", "list", "--format", "json"))

        assert_cli_runner(result)
        entries = listed(result)
        assert entries[custom_tap.name]["custom"] is True
        assert entries[tap.name]["custom"] is False

    def test_text_output_marks_custom_plugins(
        self,
        project: Project,  # noqa: ARG002
        custom_tap: ProjectPlugin,  # noqa: ARG002
        cli_runner: CliRunner,
    ) -> None:
        result = cli_runner.invoke(cli, ("plugin", "list"))

        assert_cli_runner(result)
        assert "CUSTOM" in result.stdout
        assert CUSTOM in result.stdout

    def test_mappings_are_not_listed(
        self,
        project: Project,  # noqa: ARG002
        mapper: ProjectPlugin,
        cli_runner: CliRunner,
    ) -> None:
        result = cli_runner.invoke(cli, ("plugin", "list", "--format", "json"))

        assert_cli_runner(result)
        entries = json.loads(result.stdout)
        # The mapper defines two mappings, which are configuration for it
        # rather than separate installations.
        mappers = [entry for entry in entries if entry["type"] == "mapper"]
        assert [entry["name"] for entry in mappers] == [mapper.name]


RELEASE = PluginUpdate(("pip_url",), "tap-mock==1.0", "tap-mock==2.0")
DEFINITION = PluginUpdate(("settings",), "tap-mock==1.0", "tap-mock==1.0")
LATEST = PluginUpdate((), "tap-mock==1.0", "tap-mock==1.0")


class TestPluginListUpdates:
    @pytest.mark.parametrize(
        ("update", "status"),
        ((RELEASE, "available"), (LATEST, "latest")),
    )
    def test_json_reports_the_update(
        self,
        project: Project,  # noqa: ARG002
        tap: ProjectPlugin,
        custom_tap: ProjectPlugin,
        cli_runner: CliRunner,
        monkeypatch: pytest.MonkeyPatch,
        update: PluginUpdate,
        status: str,
    ) -> None:
        monkeypatch.setattr(
            PluginLockService,
            "check_update",
            lambda _self, plugin: None if plugin.is_custom() else update,
        )
        result = cli_runner.invoke(cli, ("plugin", "list", "--format", "json"))

        assert_cli_runner(result)
        entries = listed(result)
        assert entries[tap.name]["update_status"] == status
        assert entries[tap.name]["update"]["served_pip_url"] == update.served_pip_url
        assert entries[custom_tap.name]["update_status"] is None
        assert entries[custom_tap.name]["update"] is None

    @pytest.mark.parametrize(
        ("update", "mark"),
        (
            (RELEASE, "\u2191 available"),
            (DEFINITION, "\u2191 available"),
            (LATEST, None),
            (None, None),
        ),
    )
    def test_text_output_shows_an_update(
        self,
        project: Project,  # noqa: ARG002
        tap: ProjectPlugin,
        cli_runner: CliRunner,
        monkeypatch: pytest.MonkeyPatch,
        update: PluginUpdate | None,
        mark: str | None,
    ) -> None:
        monkeypatch.setattr(
            PluginLockService,
            "check_update",
            lambda _self, _plugin: update,
        )
        result = cli_runner.invoke(cli, ("plugin", "list"))

        assert_cli_runner(result)
        assert ("UPDATE" in result.stdout) is (mark is not None)
        assert ("meltano add <type> <name>" in result.stderr) is (mark is not None)
        row = next(
            line for line in result.stdout.splitlines() if f" {tap.name} " in line
        )
        assert row.rstrip().endswith(mark or tap.variant)
