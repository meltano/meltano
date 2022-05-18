import json

from asynctest import CoroutineMock, mock

from asserts import assert_cli_runner
from meltano.cli import cli


class TestCliConfig:
    def test_config(self, project, cli_runner, tap, project_plugins_service):
        with mock.patch(
            "meltano.cli.config.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, ["config", tap.name])
            assert_cli_runner(result)

            json_config = json.loads(result.stdout)
            assert json_config["test"] == "mock"

    def test_config_extras(self, project, cli_runner, tap, project_plugins_service):
        with mock.patch(
            "meltano.cli.config.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, ["config", "--extras", tap.name])
            assert_cli_runner(result)

            json_config = json.loads(result.stdout)
            assert "_select" in json_config

    def test_config_env(self, project, cli_runner, tap, project_plugins_service):
        with mock.patch(
            "meltano.cli.config.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, ["config", "--format=env", tap.name])
            assert_cli_runner(result)

            assert 'TAP_MOCK_TEST="mock"' in result.stdout

    def test_config_meltano(
        self, project, cli_runner, engine_uri, project_plugins_service
    ):
        with mock.patch(
            "meltano.cli.config.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, ["config", "meltano"])
            assert_cli_runner(result)

            json_config = json.loads(result.stdout)
            assert json_config["send_anonymous_usage_stats"] is True
            assert json_config["database_uri"] == engine_uri
            assert json_config["cli"]["log_level"] == "info"

    def test_config_test(self, project, cli_runner, tap, project_plugins_service):

        mock_invoke = mock.Mock()
        mock_invoke.sterr.at_eof.side_effect = True
        mock_invoke.stdout.at_eof.side_effect = (False, True)
        mock_invoke.wait = CoroutineMock(return_value=0)
        mock_invoke.returncode = 0
        payload = json.dumps({"type": "RECORD"}).encode()
        mock_invoke.stdout.readline = CoroutineMock(return_value=b"%b" % payload)

        with mock.patch(
            "meltano.core.plugin_test_service.PluginInvoker.invoke_async",
            return_value=mock_invoke,
        ) as mocked_invoke:
            with mock.patch(
                "meltano.cli.config.ProjectPluginsService",
                return_value=project_plugins_service,
            ):
                result = cli_runner.invoke(cli, ["config", tap.name, "test"])
                assert mocked_invoke.assert_called_once
                assert_cli_runner(result)

                assert "Plugin configuration is valid" in result.stdout

    def test_config_meltano_test(self, project, cli_runner):
        result = cli_runner.invoke(cli, ["config", "meltano", "test"])

        assert result.exit_code == 1
        assert (
            str(result.exception)
            == "Testing of the Meltano project configuration is not supported"
        )
