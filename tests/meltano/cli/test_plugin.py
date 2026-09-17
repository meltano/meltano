from __future__ import annotations

import json
import platform
import typing as t

import pytest

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.cli.plugin import (
    CUSTOM,
    FINGERPRINT_FILE,
    _canonical,
    _requirement_name,
)
from meltano.core.plugin import PluginType
from meltano.core.project_plugins_service import PluginAlreadyAddedException

if t.TYPE_CHECKING:
    from pathlib import Path

    from click.testing import CliRunner, Result

    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project
    from meltano.core.project_add_service import ProjectAddService


def site_packages_path(venv_root: Path) -> Path:
    """Build the site-packages path for the platform running the tests."""
    if platform.system() == "Windows":
        return venv_root / "Lib" / "site-packages"
    return venv_root / "lib" / "python3.12" / "site-packages"


def fake_install(
    project: Project,
    plugin: ProjectPlugin,
    *,
    version: str | None = None,
    dist_name: str | None = None,
) -> Path:
    """Make a plugin look installed, optionally with a distribution present."""
    venv_root = project.dirs.venvs(plugin.type, plugin.plugin_dir_name)
    (venv_root / FINGERPRINT_FILE).write_text("fingerprint")

    if version is not None:
        site_packages = site_packages_path(venv_root)
        site_packages.mkdir(parents=True, exist_ok=True)
        name = (dist_name or plugin.name).replace("-", "_")
        (site_packages / f"{name}-{version}.dist-info").mkdir(exist_ok=True)

    return venv_root


def listed(result: Result) -> dict[str, dict[str, t.Any]]:
    """Parse JSON output into a mapping of plugin name to its record."""
    return {entry["name"]: entry for entry in json.loads(result.stdout)}


@pytest.fixture(scope="class")
def custom_tap(project_add_service: ProjectAddService) -> ProjectPlugin:
    """A plugin that carries its own definition, rather than one from the Hub."""
    try:
        return project_add_service.add(
            PluginType.EXTRACTORS,
            "tap-custom",
            namespace="tap_custom",
            pip_url="tap-custom",
            executable="tap-custom",
        )
    except PluginAlreadyAddedException as err:
        return err.plugin


class TestRequirementName:
    @pytest.mark.parametrize(
        ("pip_url", "expected"),
        (
            ("tap-github", "tap-github"),
            ("tap-github==1.0.0", "tap-github"),
            ("tap-github>=1.0,<2", "tap-github"),
            ("tap-github[dev]", "tap-github"),
            ("tap-github ; python_version < '3.12'", "tap-github"),
            ("git+https://github.com/meltano/tap-github.git", None),
            ("-e extract/tap-github", None),
            ("./extract/tap-github", None),
            ("", None),
            (None, None),
        ),
    )
    def test_requirement_name(self, pip_url: str | None, expected: str | None) -> None:
        assert _requirement_name(pip_url) == expected

    @pytest.mark.parametrize(
        ("name", "expected"),
        (
            ("tap_github", "tap-github"),
            ("Tap.GitHub", "tap-github"),
            ("tap--github", "tap-github"),
        ),
    )
    def test_canonical(self, name: str, expected: str) -> None:
        assert _canonical(name) == expected


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


class TestPluginListNotInstalled:
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
        assert entries[tap.name]["installed"] is False
        assert entries[tap.name]["version"] is None
        assert entries[tap.name]["type"] == "extractor"
        assert entries[target.name]["type"] == "loader"

    def test_text_output_marks_state(
        self,
        project: Project,  # noqa: ARG002
        tap: ProjectPlugin,  # noqa: ARG002
        cli_runner: CliRunner,
    ) -> None:
        result = cli_runner.invoke(cli, ("plugin", "list"))

        assert_cli_runner(result)
        assert "(not installed)" in result.stdout

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


class TestPluginListInstalled:
    def test_marks_which_plugins_are_installed(
        self,
        project: Project,
        tap: ProjectPlugin,
        target: ProjectPlugin,
        cli_runner: CliRunner,
    ) -> None:
        fake_install(project, tap)

        result = cli_runner.invoke(cli, ("plugin", "list", "--format", "json"))

        assert_cli_runner(result)
        entries = listed(result)
        assert entries[tap.name]["installed"] is True
        assert entries[target.name]["installed"] is False

    def test_reports_the_installed_version(
        self,
        project: Project,
        tap: ProjectPlugin,
        cli_runner: CliRunner,
    ) -> None:
        fake_install(project, tap, version="1.2.3")

        result = cli_runner.invoke(cli, ("plugin", "list", "--format", "json"))

        assert_cli_runner(result)
        assert listed(result)[tap.name]["version"] == "1.2.3"

    def test_ignores_unrelated_distributions(
        self,
        project: Project,
        tap: ProjectPlugin,
        cli_runner: CliRunner,
    ) -> None:
        venv_root = fake_install(project, tap, version="1.2.3")
        # Dependencies of the plugin must not be mistaken for the plugin.
        (site_packages_path(venv_root) / "requests-2.32.3.dist-info").mkdir()

        result = cli_runner.invoke(cli, ("plugin", "list", "--format", "json"))

        assert_cli_runner(result)
        assert listed(result)[tap.name]["version"] == "1.2.3"

    def test_inherited_plugin_uses_the_parent_environment(
        self,
        project: Project,
        tap: ProjectPlugin,
        inherited_tap: ProjectPlugin,
        cli_runner: CliRunner,
    ) -> None:
        # An inheriting plugin that installs nothing of its own shares the
        # virtual environment of its parent.
        fake_install(project, tap, version="1.2.3")

        result = cli_runner.invoke(cli, ("plugin", "list", "--format", "json"))

        assert_cli_runner(result)
        entries = listed(result)
        assert entries[inherited_tap.name]["installed"] is True
        assert entries[inherited_tap.name]["version"] == "1.2.3"
        assert entries[inherited_tap.name]["inherit_from"] == tap.name
        # The variant is resolved through the parent.
        assert entries[inherited_tap.name]["variant"] == entries[tap.name]["variant"]

    def test_text_output_lists_the_plugin(
        self,
        project: Project,
        tap: ProjectPlugin,
        cli_runner: CliRunner,
    ) -> None:
        fake_install(project, tap, version="1.2.3")

        result = cli_runner.invoke(cli, ("plugin", "list"))

        assert_cli_runner(result)
        assert tap.name in result.stdout
        assert "1.2.3" in result.stdout
        assert "extractor" in result.stdout


class TestPluginListWithoutDistribution:
    """A separate class, so the project has no distributions from other tests."""

    def test_version_is_none_without_a_distribution(
        self,
        project: Project,
        tap: ProjectPlugin,
        cli_runner: CliRunner,
    ) -> None:
        fake_install(project, tap)

        result = cli_runner.invoke(cli, ("plugin", "list", "--format", "json"))

        assert_cli_runner(result)
        entry = listed(result)[tap.name]
        assert entry["installed"] is True
        assert entry["version"] is None
