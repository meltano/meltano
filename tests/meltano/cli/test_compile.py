"""Test the compile CLI command."""

from __future__ import annotations

import json
import shutil
import typing as t
from pathlib import Path
from platform import system

import mock
import pytest

from meltano.cli import cli
from meltano.core.manifest import manifest

if t.TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_structlog import StructuredLogCapture

    from meltano.core.project import Project

schema_path = manifest.MANIFEST_SCHEMA_PATH


def check_indent(json_path: Path, indent: int) -> None:
    text = json_path.read_text()
    # If the indent is as-expected, then a trip through `json.loads` and
    # `json.dumps` should produce the same text, usually. This isn't true in
    # general, but it's sufficient for our use in the tests here.
    assert json.dumps(json.loads(text), indent=indent if indent > 0 else None) == text


class TestCompile:
    @pytest.fixture()
    def manifest_dir(self, project: Project) -> Path:
        return project.sys_dir_root / "manifests"

    @pytest.fixture(autouse=True)
    def clear_default_manifest_dir(self, manifest_dir: Path) -> None:
        shutil.rmtree(manifest_dir, ignore_errors=True)

    def test_compile(self, manifest_dir: Path, cli_runner: CliRunner) -> None:
        assert cli_runner.invoke(cli, ("compile",)).exit_code == 0
        assert {x.name for x in manifest_dir.iterdir()} == {
            f"meltano-manifest{x}.json" for x in (".dev", ".staging", ".prod", "")
        }

    @pytest.mark.parametrize("environment_name", ("dev", "staging", "prod"))
    def test_compile_specific_environment(
        self,
        manifest_dir: Path,
        cli_runner: CliRunner,
        environment_name: str,
    ) -> None:
        result = cli_runner.invoke(cli, ("--environment", environment_name, "compile"))
        assert result.exit_code == 0
        assert {x.name for x in manifest_dir.iterdir()} == {
            f"meltano-manifest.{environment_name}.json",
        }

    def test_compile_no_environment(
        self,
        manifest_dir: Path,
        cli_runner: CliRunner,
    ) -> None:
        result = cli_runner.invoke(cli, ("--no-environment", "compile"))
        assert result.exit_code == 0
        assert {x.name for x in manifest_dir.iterdir()} == {"meltano-manifest.json"}

    @pytest.mark.parametrize("indent", (-3, -1, 0, 1, 4, 9))
    def test_compile_with_indent(
        self,
        manifest_dir: Path,
        cli_runner: CliRunner,
        indent: int,
    ) -> None:
        assert (
            cli_runner.invoke(
                cli,
                ("--environment=dev", "compile", f"--indent={indent}"),
            ).exit_code
            == 0
        )
        check_indent(manifest_dir / "meltano-manifest.dev.json", indent)

    def test_specify_output_dir(
        self,
        manifest_dir: Path,
        cli_runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        result = cli_runner.invoke(cli, ("compile", "--directory", tmp_path))
        assert result.exit_code == 0
        assert not manifest_dir.exists()
        assert {x.name for x in tmp_path.iterdir()} == {
            f"meltano-manifest{x}.json" for x in (".dev", ".staging", ".prod", "")
        }

    def test_warn_schema_violation(
        self,
        project: Project,
        cli_runner: CliRunner,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        log: StructuredLogCapture,
    ) -> None:
        original_yaml_load = manifest.yaml.load

        def patch(*args, **kwargs):
            project_files = original_yaml_load(*args, **kwargs)
            project_files["invalid_key"] = None
            return project_files

        monkeypatch.setenv("NO_COLOR", "1")

        with mock.patch.object(manifest.yaml, "load", side_effect=patch):
            result = cli_runner.invoke(
                cli,
                ("--environment=dev", "compile", "--lint", f"--directory={tmp_path}"),
            )
        assert result.exit_code == 0
        if system() == "Windows":
            # The log message is slightly different on Windows; this length
            # check is good enough:
            assert len(log.events) == 2
            return
        assert log.events == [
            {
                "event": (
                    f"Failed to validate project files against Meltano "
                    f"manifest schema ({schema_path}):\nSchema validation "
                    "errors were encountered.\n  "
                    f"{project.root / 'meltano.yml'}::$: Additional properties"
                    " are not allowed ('invalid_key' was unexpected)"
                ),
                "level": "warning",
            },
            {
                "event": (
                    "Failed to validate newly compiled manifest against "
                    f"Meltano manifest schema ({schema_path}):\nSchema "
                    "validation errors were encountered.\n  "
                    f"{tmp_path / 'meltano-manifest.dev.json'}::$: Additional "
                    "properties are not allowed ('invalid_key' was unexpected)"
                ),
                "level": "warning",
            },
        ]
