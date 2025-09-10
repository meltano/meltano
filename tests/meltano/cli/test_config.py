from __future__ import annotations

import io
import json
import typing as t
from signal import SIGTERM
from unittest import mock
from unittest.mock import AsyncMock

import dotenv
import pytest

from asserts import assert_cli_runner
from meltano.cli import cli
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
            f"secure [env: TAP_MOCK_SECURE] current value: {REDACTED_VALUE} (from the "
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
            f"secure [env: TAP_MOCK_INHERITED_SECURE] current value: {REDACTED_VALUE} "
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
            f"secure [env: TAP_MOCK_SECURE] current value: '{value}' (from the "
            "TAP_MOCK_SECURE variable in `.env`)"
        ) in result.stdout


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
