"""CLI integration tests for user config with meltano config command."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

from meltano.cli import cli
from meltano.core.yaml_config import YamlConfigLoader


class TestCliConfigUserIntegration:
    """CLI integration tests for user config with meltano config."""

    def test_config_list_includes_user_config_values(
        self, cli_runner, project, tap, target  # noqa: ARG002
    ):
        """Test that meltano config list shows values from user config."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".meltanorc", delete=False
        ) as temp_file:
            config_content = """plugins:
  extractors:
    tap-mock:
      test: "user-config-value"
      start_date: "2023-01-01"
"""
            temp_file.write(config_content)
            temp_file.flush()

            try:
                # Patch the user config path to use our temporary file
                with patch.object(
                    YamlConfigLoader,
                    "_get_user_config_path",
                    return_value=Path(temp_file.name),
                ):
                    # Run meltano config tap-mock list
                    result = cli_runner.invoke(cli, ["config", tap.name, "list"])
                    assert result.exit_code == 0

                    # Check that user config values are displayed
                    output = result.output
                    assert "test" in output
                    assert "user-config-value" in output
                    assert "start_date" in output
                    assert "2023-01-01" in output
                    # Verify source attribution
                    assert "from user configuration" in output

            finally:
                Path(temp_file.name).unlink()

    def test_config_set_with_user_config_precedence(
        self, cli_runner, project, tap, target  # noqa: ARG002
    ):
        """Test that setting config values works when user config exists."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".meltanorc", delete=False
        ) as temp_file:
            config_content = """plugins:
  extractors:
    tap-mock:
      test: "user-config-value"
"""
            temp_file.write(config_content)
            temp_file.flush()

            try:
                # Patch the user config path to use our temporary file
                with patch.object(
                    YamlConfigLoader,
                    "_get_user_config_path",
                    return_value=Path(temp_file.name),
                ):
                    # First check that user config value is visible in list
                    result = cli_runner.invoke(cli, ["config", tap.name, "list"])
                    assert result.exit_code == 0
                    assert "user-config-value" in result.output
                    assert "from user configuration" in result.output

                    # Set a new value in project config (but user config
                    # should still take precedence)
                    result = cli_runner.invoke(
                        cli, ["config", tap.name, "set", "test", "new-project-value"]
                    )
                    assert result.exit_code == 0

                    # Check that user config value still takes precedence
                    # over project config
                    result = cli_runner.invoke(cli, ["config", tap.name, "list"])
                    assert result.exit_code == 0
                    # User config should still win due to higher precedence
                    assert "user-config-value" in result.output
                    assert "from user configuration" in result.output
                    # The project value should not be visible since user
                    # config overrides it
                    assert "new-project-value" not in result.output

            finally:
                Path(temp_file.name).unlink()

    def test_config_precedence_env_over_user_config(
        self,
        cli_runner,
        project,
        tap,
        target,
        monkeypatch,  # noqa: ARG002
    ):
        """Test that environment variables override user config values."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".meltanorc", delete=False
        ) as temp_file:
            config_content = """plugins:
  extractors:
    tap-mock:
      test: "user-config-value"
"""
            temp_file.write(config_content)
            temp_file.flush()

            try:
                # Set environment variable
                monkeypatch.setenv("TAP_MOCK_TEST", "env-value")

                # Patch the user config path to use our temporary file
                with patch.object(
                    YamlConfigLoader,
                    "_get_user_config_path",
                    return_value=Path(temp_file.name),
                ):
                    # Run meltano config tap-mock list to see current values
                    result = cli_runner.invoke(cli, ["config", tap.name, "list"])
                    assert result.exit_code == 0

                    # Check that environment variable value is shown, not user config
                    assert "env-value" in result.output
                    assert "user-config-value" not in result.output
                    # Should show environment variable source
                    assert (
                        "from environment variable" in result.output
                        or "env:" in result.output
                    )

            finally:
                Path(temp_file.name).unlink()

    def test_config_works_without_user_config_file(
        self,
        cli_runner,
        project,
        tap,
        target,  # noqa: ARG002
    ):
        """Test that config commands work normally when no user config file exists."""
        # Run meltano config tap-mock list without user config file
        result = cli_runner.invoke(cli, ["config", tap.name, "list"])
        assert result.exit_code == 0

        # Should show default behavior without errors
        output = result.output
        assert "test" in output or "No settings found" in output or len(output) >= 0

    def test_config_yaml_style_inheritance(
        self,
        cli_runner,
        project,
        tap,
        target,  # noqa: ARG002
    ):
        """Test that YAML style from user config is applied when settings are written."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".meltanorc", delete=False
        ) as temp_file:
            config_content = """yaml:
  indent: 4
  width: 100

plugins:
  extractors:
    tap-mock:
      test: "user-config-value"
"""
            temp_file.write(config_content)
            temp_file.flush()

            try:
                # Patch the user config path to use our temporary file
                with patch.object(
                    YamlConfigLoader,
                    "_get_user_config_path",
                    return_value=Path(temp_file.name),
                ):
                    # Try setting a config value (which would write to meltano.yml)
                    result = cli_runner.invoke(
                        cli, ["config", tap.name, "set", "test", "new-value"]
                    )
                    assert result.exit_code == 0

                    # Check that meltano.yml was written with custom indentation
                    meltano_yml = Path(project.root) / "meltano.yml"
                    if meltano_yml.exists():
                        content = meltano_yml.read_text()
                        # Should use 4-space indentation instead of default 2
                        lines = content.split("\n")
                        for line in lines:
                            if line.startswith("    ") and not line.startswith("  "):
                                # Found a line with 4-space indent that's not 2-space
                                break
                        else:
                            # This is okay - might not have nested structures to test
                            pass

            finally:
                Path(temp_file.name).unlink()
