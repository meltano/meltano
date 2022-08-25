from __future__ import annotations

import asyncio
import json
import platform

import mock
import pytest
from click.testing import CliRunner
from mock import AsyncMock, Mock, patch

from meltano.cli import cli
from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin.singer import SingerTap
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService


@pytest.fixture(scope="class")
def project_tap_mock(project_add_service):
    return project_add_service.add(PluginType.EXTRACTORS, "tap-mock")


@pytest.mark.usefixtures("project_tap_mock")
class TestCliInvoke:
    @pytest.fixture
    def mock_invoke(self, utility, plugin_invoker_factory):

        process_mock = Mock()
        process_mock.name = "utility-mock"
        process_mock.wait = AsyncMock(return_value=0)

        with patch(
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

    @pytest.fixture
    def mock_invoke_containers(self, utility, plugin_invoker_factory):
        with patch(
            "meltano.core.plugin_invoker.invoker_factory",
            return_value=plugin_invoker_factory,
        ), patch.object(
            ProjectPluginsService, "find_plugin", return_value=utility
        ), mock.patch(
            "aiodocker.Docker",
            autospec=True,
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

    def test_invoke_command_containerized(  # noqa: WPS210
        self,
        project,
        cli_runner,
        mock_invoke_containers,
    ):
        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
            )

        async def async_generator(*args, **kwargs):
            yield "Line 1"
            yield "Line 2"  # noqa: WPS354

        docker = mock_invoke_containers.return_value
        docker_context = mock.AsyncMock()
        docker.__aenter__.return_value = docker_context  # noqa: WPS609

        container = mock.AsyncMock()
        docker_context.containers.run.return_value = container

        container.log = mock.Mock()
        container.log.return_value = async_generator()
        container.show.return_value = {"State": {"ExitCode": 0}}

        res = cli_runner.invoke(
            cli,
            ["invoke", "--containers", "utility-mock:containerized"],
            env={"SOME_ENV": "value"},
        )

        assert res.exit_code == 0, f"exit code: {res.exit_code} - {res.exception}"
        docker_context.containers.run.assert_called_once()
        container.log.assert_called_once()
        container.wait.assert_called_once()
        container.show.assert_called_once()
        container.delete.assert_called_once()

        args, kwargs = docker_context.containers.run.call_args
        container_config = args[0]
        assert container_config["Cmd"] is None
        assert container_config["Image"] == "mock-utils/mock"
        assert "SOME_ENV=value" in container_config["Env"]

        port_bindings = container_config["HostConfig"]["PortBindings"]
        assert port_bindings == {
            "5000": [{"HostPort": "5000", "HostIP": "0.0.0.0"}]  # noqa: S104
        }

        exposed_ports = container_config["ExposedPorts"]
        assert exposed_ports == {"5000": {}}

        # Check volume env var expansion
        volume_binds = container_config["HostConfig"]["Binds"]
        assert str(project.root) in volume_binds[0]

        assert kwargs["name"].startswith("meltano-utility-mock--containerized")

        # Check env var expansion in volumes
        volume_bindings = args[0]["HostConfig"]["Binds"]
        assert volume_bindings[0].startswith(str(project.root))

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
        process_mock.wait = AsyncMock(return_value=2)

        with patch(
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

    def test_invoke_triggers(
        self,
        cli_runner: CliRunner,
        project_plugins_service: ProjectPluginsService,
        project: Project,
        tap: ProjectPlugin,
    ):
        with patch(
            "meltano.cli.invoke.ProjectPluginsService",
            return_value=project_plugins_service,
        ), patch.object(
            SingerTap, "discover_catalog"
        ) as discover_catalog, patch.object(
            SingerTap, "apply_catalog_rules"
        ) as apply_catalog_rules, patch.object(
            SingerTap, "look_up_state"
        ) as look_up_state:

            # Modes other than sync don't trigger discovery or applying catalog rules
            cli_runner.invoke(cli, ["invoke", tap.name, "--some-tap-option"])
            assert discover_catalog.call_count == 0
            assert apply_catalog_rules.call_count == 0
            assert look_up_state.call_count == 0
            project.clear_cache()

            # Dumping config doesn't trigger discovery or applying catalog rules
            cli_runner.invoke(cli, ["invoke", "--dump", "config", tap.name])
            assert discover_catalog.call_count == 0
            assert apply_catalog_rules.call_count == 0
            assert look_up_state.call_count == 0
            project.clear_cache()

            # Sync mode triggers discovery and applying catalog rules
            cli_runner.invoke(cli, ["invoke", tap.name])
            assert discover_catalog.call_count == 1
            assert apply_catalog_rules.call_count == 1
            assert look_up_state.call_count == 1
            project.clear_cache()

            # Dumping catalog triggers discovery and applying catalog rules
            cli_runner.invoke(cli, ["invoke", "--dump", "catalog", tap.name])
            assert discover_catalog.call_count == 2
            assert apply_catalog_rules.call_count == 2
            assert look_up_state.call_count == 2

    def test_invoke_dump_config(
        self, cli_runner, tap, project_plugins_service, plugin_settings_service_factory
    ):
        settings_service = plugin_settings_service_factory(tap)

        with patch(
            "meltano.cli.invoke.ProjectPluginsService",
            return_value=project_plugins_service,
        ), patch.object(SingerTap, "discover_catalog"), patch.object(
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
