from __future__ import annotations

import json
import logging
import platform
import typing as t
from unittest import mock
from unittest.mock import AsyncMock, Mock, patch

import pytest
import structlog

from meltano.cli import cli
from meltano.cli.invoke import _LogOutputHandler
from meltano.core.plugin import PluginType
from meltano.core.plugin.singer import SingerTap
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.project_plugins_service import ProjectPluginsService

if t.TYPE_CHECKING:
    from click.testing import CliRunner

    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project


@pytest.fixture(scope="class")
def project_tap_mock(project_add_service):
    return project_add_service.add(PluginType.EXTRACTORS, "tap-mock")


@pytest.mark.usefixtures("project_tap_mock")
class TestCliInvoke:
    @pytest.fixture
    def mock_invoke(self, utility: ProjectPlugin, plugin_invoker_factory):
        process_mock = Mock()
        process_mock.name = "utility-mock"
        process_mock.wait = AsyncMock(return_value=0)

        with (
            patch(
                "meltano.core.plugin_invoker.invoker_factory",
                return_value=plugin_invoker_factory,
            ),
            patch.object(
                ProjectPluginsService,
                "find_plugin",
                return_value=utility,
            ),
            patch("meltano.core.plugin_invoker.asyncio") as asyncio_mock,
        ):
            invoke_async = AsyncMock(return_value=process_mock)
            asyncio_mock.create_subprocess_exec = invoke_async
            yield invoke_async

    @pytest.fixture
    def mock_invoke_containers(self, utility: ProjectPlugin, plugin_invoker_factory):
        with (
            patch(
                "meltano.core.plugin_invoker.invoker_factory",
                return_value=plugin_invoker_factory,
            ),
            patch.object(
                ProjectPluginsService,
                "find_plugin",
                return_value=utility,
            ),
            mock.patch(
                "aiodocker.Docker",
                autospec=True,
            ) as invoke_async,
        ):
            yield invoke_async

    def test_invoke(self, cli_runner: CliRunner, mock_invoke: AsyncMock) -> None:
        res = cli_runner.invoke(cli, ["invoke", "utility-mock"])

        assert res.exit_code == 0, f"exit code: {res.exit_code} - {res.exception}"
        mock_invoke.assert_called_once()
        args, kwargs = mock_invoke.call_args
        assert args[0].endswith("utility-mock")
        assert isinstance(kwargs, dict)

    def test_invoke_args(self, cli_runner: CliRunner, mock_invoke: AsyncMock) -> None:
        res = cli_runner.invoke(cli, ["invoke", "utility-mock", "--help"])

        assert res.exit_code == 0, f"exit code: {res.exit_code} - {res.exception}"
        mock_invoke.assert_called_once()
        args = mock_invoke.call_args[0]
        assert args[0].endswith("utility-mock")
        assert args[1] == "--help"

    def test_invoke_command(
        self, cli_runner: CliRunner, mock_invoke: AsyncMock
    ) -> None:
        res = cli_runner.invoke(
            cli,
            ["invoke", "utility-mock:cmd"],
            env={"ENV_VAR_ARG": "arg"},
        )

        assert res.exit_code == 0, f"exit code: {res.exit_code} - {res.exception}"
        mock_invoke.assert_called_once()

        args = mock_invoke.call_args[0]
        assert args[0].endswith("utility-mock")
        assert args[1:] == ("--option", "arg")

    def test_invoke_command_containerized(
        self,
        project: Project,
        cli_runner: CliRunner,
        mock_invoke_containers: AsyncMock,
    ) -> None:
        if platform.system() == "Windows":
            pytest.xfail(
                "Fails on Windows: https://github.com/meltano/meltano/issues/3444",
            )

        async def async_generator(*args, **kwargs):  # noqa: ARG001
            yield "Line 1"
            yield "Line 2"

        docker = mock_invoke_containers.return_value
        docker_context = mock.AsyncMock()
        docker.__aenter__.return_value = docker_context

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
            "5000": [{"HostPort": "5000", "HostIP": "0.0.0.0"}],  # noqa: S104
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

    def test_invoke_command_args(
        self,
        cli_runner: CliRunner,
        mock_invoke: AsyncMock,
    ) -> None:
        res = cli_runner.invoke(
            cli,
            ["invoke", "utility-mock:cmd"],
            env={"ENV_VAR_ARG": "arg"},
        )

        assert res.exit_code == 0, f"exit code: {res.exit_code} - {res.exception}"
        mock_invoke.assert_called_once()

        args = mock_invoke.call_args[0]
        assert args[0].endswith("utility-mock")
        assert args[1:] == ("--option", "arg")

    def test_invoke_exit_code(
        self, cli_runner: CliRunner, mock_invoke: AsyncMock
    ) -> None:
        mock_invoke.return_value.wait.return_value = 2

        basic = cli_runner.invoke(cli, ["invoke", "utility-mock"])
        assert basic.exit_code == 2

    def test_invoke_triggers(
        self,
        cli_runner: CliRunner,
        project: Project,
        tap: ProjectPlugin,
    ) -> None:
        with (
            patch.object(SingerTap, "discover_catalog") as discover_catalog,
            patch.object(SingerTap, "apply_catalog_rules") as apply_catalog_rules,
            patch.object(SingerTap, "look_up_state") as look_up_state,
        ):
            # Modes other than sync don't trigger discovery or applying catalog rules
            cli_runner.invoke(cli, ["invoke", tap.name, "--some-tap-option"])
            assert discover_catalog.call_count == 0
            assert apply_catalog_rules.call_count == 0
            assert look_up_state.call_count == 0
            project.refresh()

            # Dumping config doesn't trigger discovery or applying catalog rules
            cli_runner.invoke(cli, ["invoke", "--dump", "config", tap.name])
            assert discover_catalog.call_count == 0
            assert apply_catalog_rules.call_count == 0
            assert look_up_state.call_count == 0
            project.refresh()

            # Sync mode triggers discovery and applying catalog rules
            cli_runner.invoke(cli, ["invoke", tap.name])
            assert discover_catalog.call_count == 1
            assert apply_catalog_rules.call_count == 1
            assert look_up_state.call_count == 1
            project.refresh()

            # Dumping catalog triggers discovery and applying catalog rules
            cli_runner.invoke(cli, ["invoke", "--dump", "catalog", tap.name])
            assert discover_catalog.call_count == 2
            assert apply_catalog_rules.call_count == 2
            assert look_up_state.call_count == 2

    def test_invoke_dump_config(
        self,
        cli_runner: CliRunner,
        tap: ProjectPlugin,
        plugin_settings_service_factory,
    ) -> None:
        settings_service = plugin_settings_service_factory(tap)

        with (
            patch.object(SingerTap, "discover_catalog"),
            patch.object(SingerTap, "apply_catalog_rules"),
        ):
            result = cli_runner.invoke(cli, ["invoke", "--dump", "config", tap.name])

            assert json.loads(result.stdout) == settings_service.as_dict(
                extras=False,
                process=True,
            )

    def test_list_commands(self, cli_runner: CliRunner, mock_invoke: AsyncMock) -> None:
        res = cli_runner.invoke(cli, ["invoke", "--list-commands", "utility-mock"])

        assert res.exit_code == 0, f"exit code: {res.exit_code} - {res.exception}"
        mock_invoke.assert_not_called()
        assert "utility-mock:cmd" in res.output
        assert "description of utility command" in res.output

    def test_invoke_only_install(
        self,
        cli_runner: CliRunner,
        project: Project,
        utility: ProjectPlugin,
    ) -> None:
        with (
            patch.object(
                ProjectPluginsService,
                "find_plugin",
                return_value=utility,
            ),
            patch("meltano.cli.params.install_plugins") as mock_install,
            patch("meltano.cli.invoke._invoke") as mock_invoke,
        ):
            res = cli_runner.invoke(cli, ["invoke", "--only-install", "utility-mock"])

        assert res.exit_code == 0, f"exit code: {res.exit_code} - {res.exception}"
        mock_install.assert_called_once_with(
            project,
            [utility],
            reason=PluginInstallReason.INSTALL,
        )
        mock_invoke.assert_not_called()


class TestLogOutputHandler:
    """Tests for the _LogOutputHandler class."""

    def test_writeline_with_singer_sdk_log(self, caplog: pytest.LogCaptureFixture):
        """Test parsing Singer SDK structured logs."""
        logger = structlog.stdlib.get_logger("test")
        handler = _LogOutputHandler(logger, log_parser="singer-sdk")

        singer_log = json.dumps(
            {
                "level": "info",
                "pid": 123,
                "logger_name": "tap-test",
                "ts": 1234567890.0,
                "thread_name": "MainThread",
                "app_name": "singer-sdk",
                "stream_name": None,
                "message": "Test message",
                "extra": {"custom": "value"},
            },
        )

        with caplog.at_level(logging.INFO):
            handler.writeline(singer_log)

        # Check that the log was parsed and the message was extracted
        assert any("Test message" in record.message for record in caplog.records)

    def test_writeline_with_unparseable_log(self, caplog: pytest.LogCaptureFixture):
        """Test fallback for unparseable logs."""
        logger = structlog.stdlib.get_logger("test")
        handler = _LogOutputHandler(logger, log_parser="singer-sdk")

        plain_log = "This is a plain text log line"

        with caplog.at_level(logging.INFO):
            handler.writeline(plain_log)

        # Check that the plain log was passed through
        assert any(
            "This is a plain text log line" in record.message
            for record in caplog.records
        )

    def test_writeline_without_parser(self, caplog: pytest.LogCaptureFixture):
        """Test that logs work without a parser configured."""
        logger = structlog.stdlib.get_logger("test")
        handler = _LogOutputHandler(logger, log_parser=None)

        log_line = "Simple log message"

        with caplog.at_level(logging.INFO):
            handler.writeline(log_line)

        # Check that the log was written
        assert any("Simple log message" in record.message for record in caplog.records)

    def test_writeline_empty_line(self, caplog: pytest.LogCaptureFixture):
        """Test that empty lines are ignored."""
        logger = structlog.stdlib.get_logger("test")
        handler = _LogOutputHandler(logger, log_parser=None)

        with caplog.at_level(logging.INFO):
            handler.writeline("")
            handler.writeline("   ")

        # No logs should be written for empty lines
        assert len(caplog.records) == 0

    def test_writeline_with_different_log_levels(
        self,
        caplog: pytest.LogCaptureFixture,
    ):
        """Test parsing logs with different severity levels."""
        logger = structlog.stdlib.get_logger("test")
        handler = _LogOutputHandler(logger, log_parser="singer-sdk")

        error_log = json.dumps(
            {
                "level": "error",
                "pid": 123,
                "logger_name": "tap-test",
                "ts": 1234567890.0,
                "thread_name": "MainThread",
                "app_name": "singer-sdk",
                "stream_name": None,
                "message": "Error occurred",
                "extra": {},
            },
        )
        warning_log = json.dumps(
            {
                "level": "warning",
                "pid": 123,
                "logger_name": "tap-test",
                "ts": 1234567890.0,
                "thread_name": "MainThread",
                "app_name": "singer-sdk",
                "stream_name": None,
                "message": "Warning message",
                "extra": {},
            },
        )

        with caplog.at_level(logging.WARNING):
            handler.writeline(error_log)
            handler.writeline(warning_log)

        # Check that both error and warning were logged
        error_record = next(
            (record for record in caplog.records if "Error occurred" in record.message),
            None,
        )
        assert error_record is not None
        assert error_record.levelname == "ERROR"

        warning_record = next(
            (
                record
                for record in caplog.records
                if "Warning message" in record.message
            ),
            None,
        )
        assert warning_record is not None
        assert warning_record.levelname == "WARNING"

    def test_writeline_preserves_extra_fields(self, caplog: pytest.LogCaptureFixture):
        """Test that extra fields from parsed logs are preserved."""
        logger = structlog.stdlib.get_logger("test")
        handler = _LogOutputHandler(logger, log_parser="singer-sdk")

        log_with_extras = json.dumps(
            {
                "level": "info",
                "pid": 123,
                "logger_name": "tap-test",
                "ts": 1234567890.0,
                "thread_name": "MainThread",
                "app_name": "singer-sdk",
                "stream_name": "users",
                "message": "Processing stream",
                "extra": {"record_count": 100},
            },
        )

        with caplog.at_level(logging.INFO):
            handler.writeline(log_with_extras)

        # Verify the message was logged
        record = next(
            (
                record
                for record in caplog.records
                if "Processing stream" in record.message
            ),
            None,
        )
        assert record is not None
        assert "Processing stream" in record.message
        assert "record_count" in str(record.msg)
