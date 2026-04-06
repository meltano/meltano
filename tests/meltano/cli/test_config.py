from __future__ import annotations

import io
import json
import typing as t
import warnings
from signal import SIGTERM
from unittest import mock
from unittest.mock import AsyncMock

import dotenv
import pytest

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.cli.config import _required_label
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.settings_service import REDACTED_VALUE, SettingValueStore

if t.TYPE_CHECKING:
    from pathlib import Path

    from click.testing import CliRunner

    from fixtures.cli import MeltanoCliRunner
    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project


class TestCliConfig:
    @pytest.mark.usefixtures("project")
    def test_config(
        self,
        cli_runner: MeltanoCliRunner,
        tap,
        session,
        plugin_settings_service_factory,
    ) -> None:
        plugin_settings_service = plugin_settings_service_factory(tap)
        plugin_settings_service.set(
            "secure",
            "a-very-secure-value",
            store=SettingValueStore.DOTENV,
            session=session,
        )
        result = cli_runner.invoke(cli, ["config", "print", tap.name])
        assert_cli_runner(result)

        json_config = json.loads(result.stdout)
        assert json_config["test"] == "mock"
        assert json_config["secure"] == "*****"

    @pytest.mark.parametrize(
        "subcommand",
        (
            "list",
            "print",
            "reset",
            "set",
            "test",
            "unset",
        ),
    )
    def test_config_help_outside_project(
        self,
        cli_runner: MeltanoCliRunner,
        subcommand: str,
    ) -> None:
        """Confirm that `config <subcommand> --help` works outside of a project."""
        result = cli_runner.invoke(cli, ["config", subcommand, "--help"])
        assert_cli_runner(result)

    @pytest.mark.usefixtures("project")
    def test_config_extras(self, cli_runner, tap) -> None:
        result = cli_runner.invoke(cli, ["config", "print", "--extras", tap.name])
        assert_cli_runner(result)

        json_config = json.loads(result.stdout)
        assert "_select" in json_config

    @pytest.mark.usefixtures("project")
    def test_config_env(
        self,
        cli_runner: CliRunner,
        tap,
        session,
        plugin_settings_service_factory,
    ) -> None:
        plugin_settings_service = plugin_settings_service_factory(tap)
        plugin_settings_service.set(
            "secure",
            "a-very-secure-value",
            store=SettingValueStore.DOTENV,
            session=session,
        )
        result = cli_runner.invoke(cli, ["config", "print", "--format=env", tap.name])
        assert_cli_runner(result)

        env_config = dotenv.dotenv_values(stream=io.StringIO(result.stdout))
        assert env_config["TAP_MOCK_TEST"] == "mock"
        assert env_config["TAP_MOCK_SECURE"] == "*****"

    @pytest.mark.usefixtures("project")
    def test_config_meltano(self, cli_runner, engine_uri) -> None:
        result = cli_runner.invoke(cli, ["config", "print", "meltano"])
        assert_cli_runner(result)

        json_config = json.loads(result.stdout)
        assert json_config["database_uri"] == engine_uri
        assert json_config["cli"]["log_level"] == "info"

    @pytest.mark.usefixtures("project")
    def test_config_unknown_plugin(
        self,
        request: pytest.FixtureRequest,
        cli_runner: MeltanoCliRunner,
    ) -> None:
        result = cli_runner.invoke(
            cli,
            [
                "config",
                "print",
                f"unknown-plugin-{request.node.nodeid}",
            ],
        )
        assert result.exit_code == 1
        assert isinstance(result.exception, PluginNotFoundError)

    @pytest.mark.usefixtures("project")
    def test_config_meltano_set(self, cli_runner) -> None:
        result = cli_runner.invoke(
            cli,
            ["config", "set", "meltano", "cli.log_config", "log_config.yml"],
        )
        assert_cli_runner(result)
        assert (
            "Meltano setting 'cli.log_config' was set in `meltano.yml`: "
            "'log_config.yml'"
        ) in result.stdout

    @pytest.mark.usefixtures("project")
    @pytest.mark.parametrize("message_type", ("RECORD", "BATCH"))
    def test_config_test(self, cli_runner, tap, message_type: str) -> None:
        mock_invoke = mock.Mock()
        mock_invoke.stderr.at_eof.side_effect = True
        mock_invoke.stdout.at_eof.side_effect = (False, True)
        mock_invoke.wait = AsyncMock(return_value=-SIGTERM)
        mock_invoke.returncode = -SIGTERM
        payload = json.dumps({"type": message_type}).encode()
        mock_invoke.stdout.readline = AsyncMock(return_value=b"%b" % payload)

        with mock.patch(
            "meltano.core.plugin_invoker.PluginInvoker.invoke_async",
            return_value=mock_invoke,
        ) as mocked_invoke:
            result = cli_runner.invoke(cli, ["config", "test", tap.name])
            assert mocked_invoke.assert_called_once
            assert_cli_runner(result)

            assert "Plugin configuration is valid" in result.stdout

    @pytest.mark.usefixtures("project")
    def test_config_meltano_test(self, cli_runner) -> None:
        result = cli_runner.invoke(cli, ["config", "test", "meltano"])

        assert result.exit_code == 1
        assert (
            str(result.exception)
            == "Testing of the Meltano project configuration is not supported"
        )

    @pytest.mark.usefixtures("project")
    def test_config_list_redacted(
        self,
        cli_runner,
        tap,
        session,
        plugin_settings_service_factory,
    ) -> None:
        plugin_settings_service = plugin_settings_service_factory(tap)
        plugin_settings_service.set(
            "secure",
            "thisisatest",
            store=SettingValueStore.DOTENV,
            session=session,
        )

        result = cli_runner.invoke(cli, ["config", "list", tap.name])
        assert_cli_runner(result)

        assert (
            "secure (required by groups 1, 3) [env: TAP_MOCK_SECURE] current value: "
            f"{REDACTED_VALUE} (from the "
            "TAP_MOCK_SECURE variable in `.env`)"
        ) in result.stdout

    @pytest.mark.usefixtures("project")
    def test_config_list_inherited(
        self,
        cli_runner,
        tap,
        inherited_tap,
        session,
        plugin_settings_service_factory,
    ) -> None:
        plugin_settings_service = plugin_settings_service_factory(tap)
        plugin_settings_service.set(
            "secure",
            "thisisatest",
            store=SettingValueStore.DOTENV,
            session=session,
        )

        result = cli_runner.invoke(cli, ["config", "list", inherited_tap.name])
        assert_cli_runner(result)

        assert (
            "secure (required by groups 1, 3) "
            "[env: TAP_MOCK_INHERITED_SECURE] current value: "
            f"{REDACTED_VALUE} "
            f"(inherited from '{tap.name}')"
        ) in result.stdout

    @pytest.mark.usefixtures("project")
    def test_config_list_unsafe(
        self,
        cli_runner,
        tap,
        session,
        plugin_settings_service_factory,
    ) -> None:
        value = "thisisatest"

        plugin_settings_service = plugin_settings_service_factory(tap)
        plugin_settings_service.set(
            "secure",
            value,
            store=SettingValueStore.DOTENV,
            session=session,
        )

        result = cli_runner.invoke(cli, ["config", "--unsafe", "list", tap.name])
        assert_cli_runner(result)

        assert (
            f"secure (required by groups 1, 3) [env: TAP_MOCK_SECURE] "
            f"current value: '{value}' "
            "(from the TAP_MOCK_SECURE variable in `.env`)"
        ) in result.stdout

    @pytest.mark.usefixtures("project")
    def test_config_list_required_settings(self, cli_runner, tap) -> None:
        result = cli_runner.invoke(cli, ["config", "list", tap.name])
        assert_cli_runner(result)

        assert "test (required) [env:" in result.stdout
        assert "secure (required by groups 1, 3) [env:" in result.stdout
        assert "auth.username (required by group 2) [env:" in result.stdout
        assert "auth.password (required by group 2) [env:" in result.stdout
        assert "port (required by group 3) [env:" in result.stdout

        assert "start_date (required" not in result.stdout

    @pytest.mark.usefixtures("project")
    def test_config_list_group_summary(self, cli_runner, tap) -> None:
        result = cli_runner.invoke(cli, ["config", "list", tap.name])
        assert_cli_runner(result)

        assert (
            "Setting groups (one of the following combinations is required):"
        ) in result.stdout
        assert "Group 1: secure, test" in result.stdout
        assert "Group 2: auth.password, auth.username, test" in result.stdout
        assert "Group 3: port, secure, test" in result.stdout

    @pytest.mark.usefixtures("project")
    def test_config_list_meltano_no_required(self, cli_runner) -> None:
        result = cli_runner.invoke(cli, ["config", "list", "meltano"])
        assert_cli_runner(result)

        assert "(required)" not in result.stdout
        assert "Setting groups" not in result.stdout

    @pytest.mark.usefixtures("project")
    def test_config_list_single_group(self, cli_runner, tap, project) -> None:
        plugin = project.plugins.find_plugin(
            tap.name,
            plugin_type=tap.type,
            configurable=True,
        )
        original = plugin.settings_group_validation
        plugin.settings_group_validation = [["test", "secure"]]
        try:
            result = cli_runner.invoke(cli, ["config", "list", tap.name])
            assert_cli_runner(result)
        finally:
            plugin.settings_group_validation = original

        assert "Required settings: secure, test" in result.stdout
        assert "Setting groups" not in result.stdout
        assert "test (required) [env:" in result.stdout
        assert "secure (required) [env:" in result.stdout
        assert "port (required" not in result.stdout

    @pytest.mark.usefixtures("project")
    def test_config_list_sorted_sections(self, cli_runner, tap) -> None:
        result = cli_runner.invoke(cli, ["config", "list", tap.name])
        assert_cli_runner(result)

        # Section headers appear
        assert "Required:" in result.stdout
        assert "Optional:" in result.stdout

        # Configured section does not appear (no non-required settings configured)
        assert "\nConfigured:\n" not in result.stdout

        # Section order: Required before Optional
        assert result.stdout.index("Required:") < result.stdout.index("Optional:")

        # Alphabetical within Required
        assert result.stdout.index("\nauth.password") < result.stdout.index(
            "\nauth.username"
        )
        assert result.stdout.index("\nauth.username") < result.stdout.index("\nport")
        assert result.stdout.index("\nport") < result.stdout.index("\nsecure")
        assert result.stdout.index("\nsecure") < result.stdout.index("\ntest")

        # Alphabetical within Optional: extract setting names and verify sorted
        lines = result.stdout.split("\n")
        optional_idx = next(i for i, line in enumerate(lines) if line == "Optional:")
        optional_names = [
            line.split(" ")[0]
            for line in lines[optional_idx + 1 :]
            if line and not line.startswith("\t") and not line.endswith(":")
        ]
        assert optional_names == sorted(optional_names)
        assert len(optional_names) > 0

    @pytest.mark.usefixtures("project")
    def test_config_list_configured_section(
        self,
        cli_runner,
        tap,
        session,
        plugin_settings_service_factory,
    ) -> None:
        plugin_settings_service = plugin_settings_service_factory(tap)
        plugin_settings_service.set(
            "start_date",
            "2023-01-01",
            store=SettingValueStore.DOTENV,
            session=session,
        )

        try:
            result = cli_runner.invoke(cli, ["config", "list", tap.name])
            assert_cli_runner(result)

            assert "Configured:" in result.stdout
            assert result.stdout.index("Required:") < result.stdout.index("Configured:")
            assert result.stdout.index("Configured:") < result.stdout.index("Optional:")

            # start_date is in Configured, not Optional
            configured_pos = result.stdout.index("Configured:")
            optional_pos = result.stdout.index("Optional:")
            start_date_pos = result.stdout.index("\nstart_date")
            assert configured_pos < start_date_pos < optional_pos
        finally:
            plugin_settings_service.unset(
                "start_date",
                store=SettingValueStore.DOTENV,
                session=session,
            )

    @pytest.mark.usefixtures("project")
    def test_config_list_extras_sorted(
        self,
        cli_runner,
        tap,
        session,
        plugin_settings_service_factory,
    ) -> None:
        # Without custom extras: no Custom: header, just sorted built-in extras
        result = cli_runner.invoke(cli, ["config", "list", "--extras", tap.name])
        assert_cli_runner(result)

        assert "Required:" not in result.stdout
        assert "Configured:" not in result.stdout
        assert "Optional:" not in result.stdout
        assert "Custom:" not in result.stdout
        assert "_select" in result.stdout

        lines = result.stdout.strip().split("\n")
        setting_names = [
            line.split(" ")[0]
            for line in lines
            if line and not line.startswith("\t") and line[0] == "_"
        ]
        assert setting_names == sorted(setting_names)
        assert len(setting_names) > 0

        # With a custom extra: Custom: header appears
        plugin_settings_service = plugin_settings_service_factory(tap)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", "Unknown setting", RuntimeWarning)
            plugin_settings_service.set(
                "_my_custom_extra",
                "test_value",
                store=SettingValueStore.MELTANO_YML,
                session=session,
            )

        try:
            result = cli_runner.invoke(cli, ["config", "list", "--extras", tap.name])
            assert_cli_runner(result)

            assert "Custom:" in result.stdout

            custom_pos = result.stdout.index("Custom:")
            custom_extra_pos = result.stdout.index("_my_custom_extra")
            assert custom_pos < custom_extra_pos
        finally:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", "Unknown setting", RuntimeWarning)
                plugin_settings_service.unset(
                    "_my_custom_extra",
                    store=SettingValueStore.MELTANO_YML,
                    session=session,
                )

    @pytest.mark.usefixtures("project")
    def test_config_list_custom_settings(
        self,
        cli_runner,
        tap,
        session,
        plugin_settings_service_factory,
    ) -> None:
        plugin_settings_service = plugin_settings_service_factory(tap)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", "Unknown setting", RuntimeWarning)
            plugin_settings_service.set(
                "my_custom_setting",
                "custom_value",
                store=SettingValueStore.MELTANO_YML,
                session=session,
            )
            plugin_settings_service.set(
                "_my_custom_extra",
                "extra_value",
                store=SettingValueStore.MELTANO_YML,
                session=session,
            )

        try:
            result = cli_runner.invoke(cli, ["config", "list", tap.name])
            assert_cli_runner(result)

            assert "Custom, possibly unsupported by the plugin:" in result.stdout
            custom_pos = result.stdout.index(
                "Custom, possibly unsupported by the plugin:"
            )
            setting_pos = result.stdout.index("my_custom_setting")
            assert custom_pos < setting_pos

            assert (
                "Custom extras, plugin-specific options handled by Meltano:"
                in result.stdout
            )
            extras_pos = result.stdout.index(
                "Custom extras, plugin-specific options handled by Meltano:"
            )
            extra_setting_pos = result.stdout.index("_my_custom_extra")
            assert extras_pos < extra_setting_pos
        finally:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", "Unknown setting", RuntimeWarning)
                plugin_settings_service.unset(
                    "my_custom_setting",
                    store=SettingValueStore.MELTANO_YML,
                    session=session,
                )
                plugin_settings_service.unset(
                    "_my_custom_extra",
                    store=SettingValueStore.MELTANO_YML,
                    session=session,
                )

    @pytest.mark.usefixtures("project")
    def test_config_list_all_required_no_optional(
        self, cli_runner, tap, project
    ) -> None:
        plugin = project.plugins.find_plugin(
            tap.name,
            plugin_type=tap.type,
            configurable=True,
        )
        all_settings = [
            "test",
            "start_date",
            "secure",
            "port",
            "list",
            "object",
            "hidden",
            "boolean",
            "auth.username",
            "auth.password",
            "aliased",
            "stacked_env_var",
        ]
        original = plugin.settings_group_validation
        plugin.settings_group_validation = [all_settings]
        try:
            result = cli_runner.invoke(cli, ["config", "list", tap.name])
            assert_cli_runner(result)
        finally:
            plugin.settings_group_validation = original

        assert "Required:" in result.stdout
        assert "Optional:" not in result.stdout

    @pytest.mark.usefixtures("project")
    def test_config_list_extras_no_extras_available(self, cli_runner) -> None:
        result = cli_runner.invoke(cli, ["config", "list", "--extras", "meltano"])
        assert_cli_runner(result)

        # meltano has no extras, so output should be empty (no sections)
        assert "Required:" not in result.stdout
        assert "Optional:" not in result.stdout
        assert "Custom:" not in result.stdout

    @pytest.mark.usefixtures("project")
    def test_config_list_sections_no_validation_groups(self, cli_runner) -> None:
        result = cli_runner.invoke(cli, ["config", "list", "meltano"])
        assert_cli_runner(result)

        assert "Required:" not in result.stdout
        assert "Optional:" in result.stdout
        assert "send_anonymous_usage_stats" in result.stdout


class TestRequiredLabel:
    @pytest.mark.parametrize(
        ("groups", "num_groups", "expected"),
        (
            ([1], 1, "required"),
            ([1, 2, 3], 3, "required"),
            ([1], 3, "required by group 1"),
            ([2], 3, "required by group 2"),
            ([1, 3], 3, "required by groups 1, 3"),
            ([1, 2], 3, "required by groups 1, 2"),
        ),
    )
    def test_required_label(
        self,
        groups: list[int],
        num_groups: int,
        expected: str,
    ) -> None:
        assert _required_label(groups, num_groups) == expected


class TestCliConfigSet:
    @pytest.mark.usefixtures("project")
    def test_config_set_redacted(self, cli_runner, tap) -> None:
        result = cli_runner.invoke(
            cli,
            ["config", "set", tap.name, "secure", "thisisatest"],
        )
        assert_cli_runner(result)

        assert (
            f"Extractor '{tap.name}' setting 'secure' was set in `.env`: "
            + REDACTED_VALUE
        ) in result.stdout

    @pytest.mark.usefixtures("project")
    def test_config_set_unsafe(self, cli_runner, tap) -> None:
        value = "thisisatest"

        result = cli_runner.invoke(
            cli,
            ["config", "--unsafe", "set", tap.name, "secure", value],
        )
        assert_cli_runner(result)

        assert (
            f"Extractor '{tap.name}' setting 'secure' was set in `.env`: '{value}'"
        ) in result.stdout

    @pytest.mark.usefixtures("project")
    @pytest.mark.filterwarnings("ignore:Unknown setting 'private_key':RuntimeWarning")
    def test_config_set_from_file(self, cli_runner, tap, tmp_path: Path) -> None:
        result = cli_runner.invoke(
            cli,
            ["config", "set", tap.name, "private_key", "--from-file", "-"],
            input="content-from-stdin",
        )
        assert_cli_runner(result)

        assert (
            f"Extractor '{tap.name}' setting 'private_key' was set in `meltano.yml`: "
            "'content-from-stdin'"
        ) in result.stdout

        filepath = tmp_path.joinpath("file.txt")
        filepath.write_text("content-from-file")

        result = cli_runner.invoke(
            cli,
            ["config", "set", tap.name, "private_key", "--from-file", filepath],
        )
        assert_cli_runner(result)

        assert (
            f"Extractor '{tap.name}' setting 'private_key' was set in `meltano.yml`: "
            "'content-from-file'"
        ) in result.stdout

    @pytest.mark.usefixtures("tap")
    def test_environments_order_of_precedence(
        self,
        project: Project,
        cli_runner,
    ) -> None:
        # set base config in `meltano.yml`
        result = cli_runner.invoke(
            cli,
            ["--no-environment", "config", "set", "tap-mock", "test", "base-mock"],
        )
        assert_cli_runner(result)
        base_tap_config = next(
            (
                tap
                for tap in project.meltano["plugins"]["extractors"]
                if tap["name"] == "tap-mock"
            ),
            {},
        )
        assert base_tap_config["config"]["test"] == "base-mock"

        # set base config in `meltano.yml` -- ignore default environment
        result = cli_runner.invoke(
            cli,
            ["config", "set", "tap-mock", "test", "base-mock-no-default"],
        )
        assert_cli_runner(result)
        base_tap_config = next(
            (
                tap
                for tap in project.meltano["plugins"]["extractors"]
                if tap["name"] == "tap-mock"
            ),
            {},
        )
        assert base_tap_config["config"]["test"] == "base-mock-no-default"

        # set dev environment config in `meltano.yml`
        result = cli_runner.invoke(
            cli,
            ["--environment=dev", "config", "set", "tap-mock", "test", "dev-mock"],
        )
        assert_cli_runner(result)
        dev_env = next(
            (env for env in project.meltano["environments"] if env["name"] == "dev"),
            {},
        )
        tap_config = next(
            (
                tap
                for tap in dev_env["config"]["plugins"]["extractors"]
                if tap["name"] == "tap-mock"
            ),
            {},
        )
        assert tap_config["config"]["test"] == "dev-mock"

    def test_interactive_config_triggered(
        self,
        cli_runner: MeltanoCliRunner,
        tap: ProjectPlugin,
    ) -> None:
        """Test that the interactive config flow is triggered."""
        target = "meltano.cli.interactive.config.InteractiveConfig.configure_all"
        with mock.patch(target) as mock_configure_all:
            result = cli_runner.invoke(
                cli,
                ["config", "set", tap.name, "--interactive"],
            )
            assert_cli_runner(result)
            mock_configure_all.assert_called_once()
            mock_configure_all.reset_mock()

            result = cli_runner.invoke(cli, ["config", "set", tap.name])
            assert_cli_runner(result)
            mock_configure_all.assert_called_once()
            mock_configure_all.reset_mock()

            result = cli_runner.invoke(cli, ["config", "set"], input=f"{tap.name}\n")
            assert_cli_runner(result)
            mock_configure_all.assert_called_once()


class TestCliConfigUnset:
    @pytest.mark.usefixtures("project")
    def test_config_unset(self, cli_runner, tap) -> None:
        secure_value = "thisisatest"
        set_default_result = cli_runner.invoke(
            cli,
            ["config", "set", tap.name, "secure", secure_value],
        )
        assert_cli_runner(set_default_result)

        meltano_yml_value = "thisisatest-meltano-yml"
        set_meltano_yml_result = cli_runner.invoke(
            cli,
            [
                "config",
                "set",
                tap.name,
                "--store=meltano_yml",
                "secure",
                meltano_yml_value,
            ],
        )
        assert_cli_runner(set_meltano_yml_result)

        unset_result = cli_runner.invoke(
            cli,
            ["config", "unset", tap.name, "--store=meltano_yml", "secure"],
        )
        assert_cli_runner(unset_result)
        assert (
            f"Extractor '{tap.name}' setting 'secure' in `meltano.yml` was unset"
        ) in unset_result.stdout
        assert "Current value is now: '(redacted)'" in unset_result.stdout
