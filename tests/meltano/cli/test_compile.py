"""Test the compile CLI command."""

from __future__ import annotations

import json
import re
import shutil
import typing as t
from pathlib import Path
from platform import system
from unittest import mock

import pytest

from meltano.cli import cli
from meltano.core.manifest import manifest
from meltano.core.settings_service import REDACTED_VALUE, SettingValueStore

if t.TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_structlog import StructuredLogCapture

    from meltano.core.project import Project

schema_path = manifest.MANIFEST_SCHEMA_PATH
schema_validation_log_prefix = manifest.SCHEMA_VALIDATION_LOG_PREFIX

SECURE_VALUE = "a-very-secure-value"


def check_indent(json_path: Path, indent: int) -> None:
    text = json_path.read_text()
    # If the indent is as-expected, then a trip through `json.loads` and
    # `json.dumps` should produce the same text, usually. This isn't true in
    # general, but it's sufficient for our use in the tests here.
    assert json.dumps(json.loads(text), indent=indent if indent > 0 else None) == text


def get_schema_warnings(log: StructuredLogCapture) -> list[dict[str, t.Any]]:
    """Return schema validation warning log events."""
    return [
        e
        for e in log.events
        if e.get("level") == "warning"
        and schema_validation_log_prefix in e.get("event", "")
    ]


class TestCompile:
    @pytest.fixture
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
        tmp_path: Path,
        log: StructuredLogCapture,
    ) -> None:
        """Test schema validation warnings for root-level errors.

        This test verifies that root-level schema violations (like adding
        'invalid_key' at the top level) are reported with the '::$' format,
        indicating the error is at the document root.
        """
        original_yaml_load = manifest.yaml.load

        def patch(*args, **kwargs):
            project_files = original_yaml_load(*args, **kwargs)
            project_files["invalid_key"] = None
            return project_files

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
        assert log.events[-2:] == [
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

    def test_no_schema_violation_with_lint(
        self,
        manifest_dir: Path,
        cli_runner: CliRunner,
        log: StructuredLogCapture,
    ) -> None:
        """Test that valid schemas pass validation without warnings."""
        result = cli_runner.invoke(
            cli,
            ("--environment=dev", "compile", "--lint"),
        )
        assert result.exit_code == 0
        # Verify that no schema validation warnings were logged
        schema_warnings = get_schema_warnings(log)
        assert len(schema_warnings) == 0, (
            "Expected no schema validation warnings for valid project, "
            f"but found: {[e.get('event')[:100] for e in schema_warnings]}"
        )
        # Verify manifest files were created successfully
        assert {x.name for x in manifest_dir.iterdir()} == {
            "meltano-manifest.dev.json",
        }

    def test_warn_nested_schema_violation(
        self,
        cli_runner: CliRunner,
        tmp_path: Path,
        log: StructuredLogCapture,
    ) -> None:
        """Test schema validation warnings for nested path errors.

        This test verifies that nested schema violations (like adding a plugin
        with an invalid 'name' type) are reported with the '::$.<path>' format,
        indicating the full JSON path to the error location.
        """
        original_yaml_load = manifest.yaml.load

        def patch(*args, **kwargs):
            project_files = original_yaml_load(*args, **kwargs)
            # Create a nested schema violation by adding a plugin with invalid 'name'
            # The 'name' field should be a string, but we'll set it to an integer
            if "plugins" not in project_files:
                project_files["plugins"] = {}
            if "extractors" not in project_files["plugins"]:
                project_files["plugins"]["extractors"] = []
            # Add a plugin with an invalid name (integer instead of string)
            project_files["plugins"]["extractors"].append({"name": 12345})
            return project_files

        with mock.patch.object(manifest.yaml, "load", side_effect=patch):
            result = cli_runner.invoke(
                cli,
                ("--environment=dev", "compile", "--lint", f"--directory={tmp_path}"),
            )
        assert result.exit_code == 0
        # Filter to schema validation warnings specifically
        schema_warnings = get_schema_warnings(log)
        assert len(schema_warnings) >= 1, (
            "Expected at least one schema validation warning"
        )
        # Check that the warning contains the full nested JSON path.
        # The path should match: ::$.plugins.extractors.<index>.name
        # where <index> depends on existing extractors in the project fixture.
        expected_pattern = r"::\$\.plugins\.extractors\.\d+\.name"
        nested_path_found = any(
            re.search(expected_pattern, event.get("event", ""))
            for event in schema_warnings
        )
        assert nested_path_found, (
            f"Expected to find pattern '{expected_pattern}' in validation errors. "
            f"Events: {[e.get('event') for e in schema_warnings]}"
        )

    # First option tests default behavior.
    # The "--no-lint" flag has no effect as it is the default
    @pytest.mark.parametrize(
        ("flag", "expected_value"),
        (
            ("--no-lint", REDACTED_VALUE),
            ("--safe", REDACTED_VALUE),
            ("--unsafe", SECURE_VALUE),
        ),
    )
    def test_safe_unsafe(
        self,
        manifest_dir: Path,
        tap,
        session,
        plugin_settings_service_factory,
        cli_runner: CliRunner,
        flag: str,
        expected_value: str,
    ) -> None:
        plugin_settings_service = plugin_settings_service_factory(tap)
        plugin_settings_service.set(
            "secure",
            SECURE_VALUE,
            store=SettingValueStore.DOTENV,
            session=session,
        )

        result = cli_runner.invoke(cli, ("--no-environment", "compile", flag))
        assert result.exit_code == 0

        manifest_filepath = Path(manifest_dir) / "meltano-manifest.json"
        manifest_text = manifest_filepath.read_text()
        assert expected_value in manifest_text
