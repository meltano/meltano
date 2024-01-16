from __future__ import annotations

import json
import platform
import typing as t
from signal import SIGTERM

import pytest
from mock import AsyncMock, mock

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.settings_service import REDACTED_VALUE, SettingValueStore

if t.TYPE_CHECKING:
    from pathlib import Path

    from meltano.core.project import Project


class TestCliConfig:
    @pytest.mark.usefixtures("project")
    def test_config(self, cli_runner, tap):
        if platform.system() == "Windows":
            pytest.xfail(
                "Fails on Windows: https://github.com/meltano/meltano/issues/3444",
            )
        result = cli_runner.invoke(cli, ["config", tap.name])
        assert_cli_runner(result)

        json_config = json.loads(result.stdout)
        assert json_config["test"] == "mock"

    @pytest.mark.usefixtures("project")
    def test_config_extras(self, cli_runner, tap):
        result = cli_runner.invoke(cli, ["config", "--extras", tap.name])
        assert_cli_runner(result)

        json_config = json.loads(result.stdout)
        assert "_select" in json_config

    @pytest.mark.usefixtures("project")
    def test_config_env(self, cli_runner, tap):
        if platform.system() == "Windows":
            pytest.xfail(
                "Fails on Windows: https://github.com/meltano/meltano/issues/3444",
            )
        result = cli_runner.invoke(cli, ["config", "--format=env", tap.name])
        assert_cli_runner(result)

        assert "TAP_MOCK_TEST='mock'" in result.stdout

    @pytest.mark.usefixtures("project")
    def test_config_meltano(self, cli_runner, engine_uri):
        result = cli_runner.invoke(cli, ["config", "meltano"])
        assert_cli_runner(result)

        json_config = json.loads(result.stdout)
        assert json_config["database_uri"] == engine_uri
        assert json_config["cli"]["log_level"] == "info"

    @pytest.mark.usefixtures("project")
    def test_config_meltano_set(self, cli_runner):
        result = cli_runner.invoke(
            cli,
            ["config", "meltano", "set", "cli.log_config", "log_config.yml"],
        )
        assert_cli_runner(result)
        assert (
            "Meltano setting 'cli.log_config' was set in `meltano.yml`: "
            "'log_config.yml'"
        ) in result.stdout

    @pytest.mark.usefixtures("project")
    def test_config_test(self, cli_runner, tap):
        mock_invoke = mock.Mock()
        mock_invoke.sterr.at_eof.side_effect = True
        mock_invoke.stdout.at_eof.side_effect = (False, True)
        mock_invoke.wait = AsyncMock(return_value=-SIGTERM)
        mock_invoke.returncode = -SIGTERM
        payload = json.dumps({"type": "RECORD"}).encode()
        mock_invoke.stdout.readline = AsyncMock(return_value=b"%b" % payload)

        with mock.patch(
            "meltano.core.plugin_invoker.PluginInvoker.invoke_async",
            return_value=mock_invoke,
        ) as mocked_invoke:
            result = cli_runner.invoke(cli, ["config", tap.name, "test"])
            assert mocked_invoke.assert_called_once
            assert_cli_runner(result)

            assert "Plugin configuration is valid" in result.stdout

    @pytest.mark.usefixtures("project")
    def test_config_meltano_test(self, cli_runner):
        result = cli_runner.invoke(cli, ["config", "meltano", "test"])

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
    ):
        plugin_settings_service = plugin_settings_service_factory(tap)
        plugin_settings_service.set(
            "secure",
            "thisisatest",
            store=SettingValueStore.DOTENV,
            session=session,
        )

        result = cli_runner.invoke(cli, ["config", tap.name, "list"])
        assert_cli_runner(result)

        assert (
            f"secure [env: TAP_MOCK_SECURE] current value: {REDACTED_VALUE} (from the "
            "TAP_MOCK_SECURE variable in `.env`)"
        ) in result.stdout

    @pytest.mark.usefixtures("project")
    def test_config_list_unsafe(
        self,
        cli_runner,
        tap,
        session,
        plugin_settings_service_factory,
    ):
        value = "thisisatest"

        plugin_settings_service = plugin_settings_service_factory(tap)
        plugin_settings_service.set(
            "secure",
            value,
            store=SettingValueStore.DOTENV,
            session=session,
        )

        result = cli_runner.invoke(cli, ["config", "--unsafe", tap.name, "list"])
        assert_cli_runner(result)

        assert (
            f"secure [env: TAP_MOCK_SECURE] current value: '{value}' (from the "
            "TAP_MOCK_SECURE variable in `.env`)"
        ) in result.stdout


class TestCliConfigSet:
    @pytest.mark.usefixtures("project")
    def test_config_set_redacted(self, cli_runner, tap):
        result = cli_runner.invoke(
            cli,
            ["config", tap.name, "set", "secure", "thisisatest"],
        )
        assert_cli_runner(result)

        assert (
            f"Extractor '{tap.name}' setting 'secure' was set in `.env`: "
            + REDACTED_VALUE
        ) in result.stdout

    @pytest.mark.usefixtures("project")
    def test_config_set_unsafe(self, cli_runner, tap):
        value = "thisisatest"

        result = cli_runner.invoke(
            cli,
            ["config", "--unsafe", tap.name, "set", "secure", value],
        )
        assert_cli_runner(result)

        assert (
            f"Extractor '{tap.name}' setting 'secure' was set in `.env`: '{value}'"
        ) in result.stdout

    @pytest.mark.usefixtures("project")
    def test_config_set_from_file(self, cli_runner, tap, tmp_path: Path):
        result = cli_runner.invoke(
            cli,
            ["config", tap.name, "set", "private_key", "--from-file", "-"],
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
            ["config", tap.name, "set", "private_key", "--from-file", filepath],
        )
        assert_cli_runner(result)

        assert (
            f"Extractor '{tap.name}' setting 'private_key' was set in `meltano.yml`: "
            "'content-from-file'"
        ) in result.stdout

    @pytest.mark.usefixtures("tap")
    def test_environments_order_of_precedence(self, project: Project, cli_runner):
        # set base config in `meltano.yml`
        result = cli_runner.invoke(
            cli,
            ["--no-environment", "config", "tap-mock", "set", "test", "base-mock"],
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
            ["config", "tap-mock", "set", "test", "base-mock-no-default"],
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
            ["--environment=dev", "config", "tap-mock", "set", "test", "dev-mock"],
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
