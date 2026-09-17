from __future__ import annotations

import json
import platform
import typing as t

import pytest

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.cli.plugin import (
    CUSTOM,
    _direct_url_revision,
    _requirement_name,
    _vcs_url,
)
from meltano.core.plugin import PluginType
from meltano.core.project_plugins_service import PluginAlreadyAddedException
from meltano.core.venv_service import VirtualEnv

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


def write_dist_info(
    site_packages: Path,
    name: str,
    version: str,
    direct_url: dict[str, t.Any] | None = None,
) -> Path:
    """Write the metadata that `pip` leaves behind for a distribution."""
    dist_info = site_packages / f"{name.replace('-', '_')}-{version}.dist-info"
    dist_info.mkdir(parents=True, exist_ok=True)
    (dist_info / "METADATA").write_text(
        f"Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n",
    )

    if direct_url is not None:
        (dist_info / "direct_url.json").write_text(json.dumps(direct_url))

    return dist_info


def fake_install(
    project: Project,
    plugin: ProjectPlugin,
    *,
    version: str | None = None,
    dist_name: str | None = None,
    direct_url: dict[str, t.Any] | None = None,
) -> Path:
    """Make a plugin look installed, optionally with a distribution present."""
    venv_root = project.dirs.venvs(plugin.type, plugin.plugin_dir_name)
    VirtualEnv(venv_root).plugin_fingerprint_path.write_text("fingerprint")

    if version is not None:
        write_dist_info(
            site_packages_path(venv_root),
            dist_name or plugin.name,
            version,
            direct_url,
        )

    return venv_root


def listed(result: Result) -> dict[str, dict[str, t.Any]]:
    """Parse JSON output into a mapping of plugin name to its record."""
    return {entry["name"]: entry for entry in json.loads(result.stdout)}


@pytest.fixture(scope="class")
def repo_tap(project_add_service: ProjectAddService) -> ProjectPlugin:
    """A plugin installed from a repository at a tag, rather than from PyPI."""
    try:
        return project_add_service.add(
            PluginType.EXTRACTORS,
            "tap-repo",
            namespace="tap_repo",
            pip_url="git+https://github.com/meltano/tap-repo.git@v1.0.0",
            executable="tap-repo",
        )
    except PluginAlreadyAddedException as err:
        return err.plugin


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


class TestVcsUrl:
    @pytest.mark.parametrize(
        ("pip_url", "expected"),
        (
            (
                "git+https://github.com/meltano/tap-github.git@v1.0.0",
                "https://github.com/meltano/tap-github.git",
            ),
            (
                "git+https://github.com/meltano/tap-github.git",
                "https://github.com/meltano/tap-github.git",
            ),
            (
                "git+ssh://git@github.com/meltano/tap-github.git@main",
                "ssh://git@github.com/meltano/tap-github.git",
            ),
            (
                "git+https://user:token@github.com/meltano/tap-github.git@v1.0.0",
                "https://user:token@github.com/meltano/tap-github.git",
            ),
            (
                "git+https://github.com/meltano/tap-github.git@v1.0.0#egg=tap-github",
                "https://github.com/meltano/tap-github.git",
            ),
            ("tap-github", None),
            ("./extract/tap-github", None),
        ),
    )
    def test_vcs_url(self, pip_url: str, expected: str | None) -> None:
        assert _vcs_url(pip_url) == expected


class TestDirectUrlRevision:
    """The revision is found through the URL that `pip` recorded, not a name."""

    PIP_URL = "git+https://github.com/meltano/tap-mock.git@v1.0.0"

    @staticmethod
    def vcs_info(url: str, revision: str | None) -> dict[str, t.Any]:
        vcs_info: dict[str, t.Any] = {"vcs": "git", "commit_id": "a" * 40}
        if revision is not None:
            vcs_info["requested_revision"] = revision
        return {"url": url, "vcs_info": vcs_info}

    def test_reports_the_requested_revision(self, tmp_path: Path) -> None:
        write_dist_info(
            tmp_path,
            "meltanolabs-tap-mock",
            "0.0.0",
            self.vcs_info("https://github.com/meltano/tap-mock.git", "v1.0.0"),
        )

        assert _direct_url_revision(tmp_path, self.PIP_URL) == "v1.0.0"

    def test_ignores_another_distribution(self, tmp_path: Path) -> None:
        # A dependency installed from its own repository must not be mistaken
        # for the plugin.
        write_dist_info(
            tmp_path,
            "requests",
            "2.32.3",
            self.vcs_info("https://github.com/psf/requests.git", "v2.32.3"),
        )

        assert _direct_url_revision(tmp_path, self.PIP_URL) is None

    def test_reports_nothing_without_a_requested_revision(
        self,
        tmp_path: Path,
    ) -> None:
        write_dist_info(
            tmp_path,
            "meltanolabs-tap-mock",
            "0.0.0",
            self.vcs_info("https://github.com/meltano/tap-mock.git", None),
        )

        assert _direct_url_revision(tmp_path, self.PIP_URL) is None

    def test_reports_nothing_for_a_plain_requirement(self, tmp_path: Path) -> None:
        write_dist_info(tmp_path, "tap-mock", "1.0.0")

        assert _direct_url_revision(tmp_path, "tap-mock") is None


class TestPluginListFromRepository:
    """A separate class, so the project has no distributions from other tests."""

    def test_reports_the_revision_of_a_repository_install(
        self,
        project: Project,
        repo_tap: ProjectPlugin,
        cli_runner: CliRunner,
    ) -> None:
        fake_install(
            project,
            repo_tap,
            version="0.0.0",
            dist_name="meltanolabs_tap_repo",
            direct_url={
                "url": "https://github.com/meltano/tap-repo.git",
                "vcs_info": {
                    "vcs": "git",
                    "commit_id": "a" * 40,
                    "requested_revision": "v1.0.0",
                },
            },
        )

        result = cli_runner.invoke(cli, ("plugin", "list", "--format", "json"))

        assert_cli_runner(result)
        assert listed(result)[repo_tap.name]["version"] == "v1.0.0"


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

    def test_a_created_environment_is_not_an_install(
        self,
        project: Project,
        tap: ProjectPlugin,
        cli_runner: CliRunner,
    ) -> None:
        # An install that fails after the environment is created leaves an
        # interpreter behind, and no fingerprint.
        venv = VirtualEnv(project.dirs.venvs(tap.type, tap.plugin_dir_name))
        venv.bin_dir.mkdir(parents=True, exist_ok=True)
        (venv.bin_dir / "python").touch()

        result = cli_runner.invoke(cli, ("plugin", "list", "--format", "json"))

        assert_cli_runner(result)
        assert listed(result)[tap.name]["installed"] is False

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
        write_dist_info(site_packages_path(venv_root), "requests", "2.32.3")

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
