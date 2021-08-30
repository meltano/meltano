import asyncio
import json
from unittest.mock import Mock, patch

import pytest
from asynctest import CoroutineMock
from meltano.cli import cli
from meltano.core.plugin import PluginType
from meltano.core.plugin.singer import SingerTap
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.tracking import GoogleAnalyticsTracker


@pytest.fixture(scope="class")
def project_tap_mock(project_add_service):
    return project_add_service.add(PluginType.EXTRACTORS, "tap-mock")


@pytest.mark.usefixtures("project_tap_mock")
class TestCliInvoke:
    @pytest.fixture
    def mock_invoke(self, utility, plugin_invoker_factory):

        process_mock = Mock()
        process_mock.name = "utility-mock"
        process_mock.wait = CoroutineMock(return_value=0)

        with patch.object(
            GoogleAnalyticsTracker, "track_data", return_value=None
        ), patch(
            "meltano.core.plugin_invoker.invoker_factory",
            return_value=plugin_invoker_factory,
        ), patch.object(
            ProjectPluginsService, "find_plugin", return_value=utility
        ), patch.object(
            asyncio,
            "create_subprocess_exec",
            return_value=process_mock,
        ) as invoke_async:
            yield invoke_async

    def test_invoke(self, cli_runner, mock_invoke):
        res = cli_runner.invoke(cli, ["invoke", "utility-mock"])

        assert res.exit_code == 0, f"exit code: {res.exit_code} - {res.exception}"
        mock_invoke.assert_called_once()
        args, kwargs = mock_invoke.call_args
        assert args[0].endswith("utility-mock")
        assert isinstance(kwargs, dict)

    def test_invoke_args(self, cli_runner, mock_invoke):
        res = cli_runner.invoke(cli, ["invoke", "utility-mock", "--help"])

        assert res.exit_code == 0, f"exit code: {res.exit_code} - {res.exception}"
        mock_invoke.assert_called_once()
        args = mock_invoke.call_args[0]
        assert args[0].endswith("utility-mock")
        assert args[1] == "--help"

    def test_invoke_command(self, cli_runner, mock_invoke):
        res = cli_runner.invoke(
            cli, ["invoke", "utility-mock:cmd"], env={"ENV_VAR_ARG": "arg"}
        )

        assert res.exit_code == 0, f"exit code: {res.exit_code} - {res.exception}"
        mock_invoke.assert_called_once()

        args = mock_invoke.call_args[0]
        assert args[0].endswith("utility-mock")
        assert args[1:] == ("--option", "arg")

    def test_invoke_command_args(self, cli_runner, mock_invoke):
        res = cli_runner.invoke(
            cli, ["invoke", "utility-mock:cmd", "--verbose"], env={"ENV_VAR_ARG": "arg"}
        )

        assert res.exit_code == 0, f"exit code: {res.exit_code} - {res.exception}"
        mock_invoke.assert_called_once()

        args = mock_invoke.call_args[0]
        assert args[0].endswith("utility-mock")
        assert args[1:] == ("--option", "arg", "--verbose")

    def test_invoke_exit_code(
        self, cli_runner, tap, project_plugins_service, plugin_invoker_factory, utility
    ):
        process_mock = Mock()
        process_mock.name = "utility-mock"
        process_mock.wait = CoroutineMock(return_value=2)

        with patch.object(
            GoogleAnalyticsTracker, "track_data", return_value=None
        ), patch(
            "meltano.core.plugin_invoker.invoker_factory",
            return_value=plugin_invoker_factory,
        ), patch.object(
            ProjectPluginsService, "find_plugin", return_value=utility
        ), patch.object(
            asyncio,
            "create_subprocess_exec",
            return_value=process_mock,
        ):
            basic = cli_runner.invoke(cli, ["invoke", tap.name])
            assert basic.exit_code == 2

    def test_invoke_dump_config(
        self, cli_runner, tap, project_plugins_service, plugin_settings_service_factory
    ):
        settings_service = plugin_settings_service_factory(tap)

        with patch.object(
            GoogleAnalyticsTracker, "track_data", return_value=None
        ), patch(
            "meltano.cli.invoke.ProjectPluginsService",
            return_value=project_plugins_service,
        ), patch.object(
            SingerTap, "discover_catalog"
        ), patch.object(
            SingerTap, "apply_catalog_rules"
        ):
            result = cli_runner.invoke(cli, ["invoke", "--dump", "config", tap.name])

            assert json.loads(result.stdout) == settings_service.as_dict(
                extras=False, process=True
            )

    def test_list_commands(self, cli_runner, mock_invoke):
        res = cli_runner.invoke(cli, ["invoke", "--list-commands", "utility-mock"])

        assert res.exit_code == 0, f"exit code: {res.exit_code} - {res.exception}"
        mock_invoke.assert_not_called()
        assert "utility-mock:cmd" in res.output
        assert "description of utility command" in res.output
