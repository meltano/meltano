from __future__ import annotations

import asyncio
import json
import platform
import typing as t
from dataclasses import dataclass
from unittest import mock
from unittest.mock import AsyncMock

import pytest

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.cli.utils import CliError
from meltano.core.job import Job, State
from meltano.core.plugin import PluginType
from meltano.core.plugin.singer import SingerTap
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.project_add_service import PluginAlreadyAddedException
from meltano.core.runner.dbt import DbtRunner
from meltano.core.runner.singer import SingerRunner

if t.TYPE_CHECKING:
    from fixtures.cli import MeltanoCliRunner


@dataclass
class LogEntry:
    """Check whether a log entry is in a list of dicts.

    Attributes:
        name: The name to search for.
        cmd_type: The `cmd_type` to search for.
        event: Prefix of the event to search for.
        level: The level to search for.
        stdio: If not `None`, verify the stdio matches.
    """

    name: str | None = None
    cmd_type: str | None = None
    event: str | None = None
    level: str | None = None
    stdio: str | None = None

    def matches(self, lines: list[dict]) -> bool:
        """Find a matching log line in the provided list of log lines.

        It's important to note that the 'event' field check doesn't look for
        exact matches, and is doing a prefix search. This is because quite a
        few log lines have dynamic suffix segments.

        Args:
            lines: the log lines to check against

        Returns:
            True if a matching log line is found, else False
        """
        for line in lines:
            matches = (
                line.get("name") == self.name
                and line.get("cmd_type") == self.cmd_type
                and line.get("event").startswith(self.event)
                and line.get("level") == self.level
            )

            if matches:
                return line.get("stdio") == self.stdio if self.stdio else True

        return False  # pragma: no cover


def exception_logged(result_output: str, exc: Exception) -> bool:
    """Small utility to search click result output for a specific exception.

    Args:
        result_output: The click result output string to search.
        exc: The exception to search for.

    Returns:
        bool: Whether the exception was found
    """
    seen_lines: list[dict] = []
    for line in result_output.splitlines():
        parsed_line = json.loads(line)
        seen_lines.append(parsed_line)

    return any(
        line.get("event") and exc.args[0] in line.get("event") for line in seen_lines
    )


def assert_log_lines(result_output: str, expected: list[LogEntry]) -> None:
    seen_lines: list[dict] = []
    for line in result_output.splitlines():
        try:
            parsed_line = json.loads(line)
        except json.JSONDecodeError:  # pragma: no cover
            continue
        seen_lines.append(parsed_line)

    for entry in expected:
        assert entry.matches(seen_lines), f"Expected log entry not found: {entry}"


def failure_help_log_suffix(job_logs_file) -> str:
    return (
        "For more detailed log messages re-run the command using 'meltano "
        "--log-level=debug ...' CLI flag.\nNote that you can also check the "
        f"generated log file at '{job_logs_file}'.\nFor more information on "
        "debugging and logging: "
        "https://docs.meltano.com/reference/command-line-interface#debugging"
    )


@pytest.fixture(scope="class")
def tap_mock_transform(project_add_service):
    try:
        return project_add_service.add(PluginType.TRANSFORMS, "tap-mock-transform")
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture
def process_mock_factory():
    def _factory(name):
        process_mock = mock.Mock()
        process_mock.name = name
        process_mock.wait = AsyncMock(return_value=0)
        process_mock.returncode = 0
        process_mock.stdin.wait_closed = AsyncMock(return_value=True)
        return process_mock

    return _factory


@pytest.fixture
def tap_process(process_mock_factory, tap):
    tap = process_mock_factory(tap)
    tap.stdout.at_eof.side_effect = (False, False, False, True)
    tap.stdout.readline = AsyncMock(side_effect=(b"SCHEMA\n", b"RECORD\n", b"STATE\n"))
    tap.stderr.at_eof.side_effect = (False, False, False, True)
    tap.stderr.readline = AsyncMock(
        side_effect=(b"Starting\n", b"Running\n", b"Done\n"),
    )
    return tap


@pytest.fixture
def target_process(process_mock_factory, target):
    target = process_mock_factory(target)

    # Have `target.wait` take 1s to make sure the tap always finishes before the target
    async def wait_mock():
        await asyncio.sleep(1)
        return target.wait.return_value

    target.wait.side_effect = wait_mock

    target.stdout.at_eof.side_effect = (False, False, False, True)
    target.stdout.readline = AsyncMock(
        side_effect=(b'{"line": 1}\n', b'{"line": 2}\n', b'{"line": 3}\n'),
    )
    target.stderr.at_eof.side_effect = (False, False, False, True)
    target.stderr.readline = AsyncMock(
        side_effect=(b"Starting\n", b"Running\n", b"Done\n"),
    )
    return target


@pytest.fixture
def silent_dbt_process(process_mock_factory, dbt):
    dbt = process_mock_factory(dbt)
    dbt.stdout.at_eof.side_effect = (True, True)
    dbt.stderr.at_eof.side_effect = (True, True)
    return dbt


@pytest.fixture
def dbt_process(process_mock_factory, dbt):
    dbt = process_mock_factory(dbt)
    dbt.stdout.at_eof.side_effect = (True,)
    dbt.stderr.at_eof.side_effect = (False, False, False, True)
    dbt.stderr.readline = AsyncMock(
        side_effect=(b"Starting\n", b"Running\n", b"Done\n"),
    )
    return dbt


@pytest.fixture(autouse=True)
def mock_plugin_installation_env():
    with mock.patch.object(
        PluginInstallService,
        "plugin_installation_env",
    ) as plugin_installation_env:
        yield plugin_installation_env


class TestWindowsELT:
    @pytest.mark.skipif(
        platform.system() != "Windows",
        reason="Test is only for Windows",
    )
    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures("use_test_log_config")
    def test_elt_windows(
        self,
        cli_runner,
        tap,
        target,
    ) -> None:
        args = ["elt", tap.name, target.name]
        result = cli_runner.invoke(cli, args)
        assert result.exit_code == 1
        # Didn't use `exception_logged()` as `result.stderr` doesn't contain
        # the error for some reason
        assert (
            "ELT command not supported on Windows. Please use the run command "
            "as documented here: "
            "https://docs.meltano.com/reference/command-line-interface#run"
        ) in str(result.exception)


@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="ELT is not supported on Windows",
)
class TestCliEltScratchpadOne:
    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures("use_test_log_config", "project")
    @pytest.mark.parametrize("command", ("elt", "el"), ids=["elt", "el"])
    def test_elt(
        self,
        cli_runner,
        tap,
        target,
        tap_process,
        target_process,
        job_logging_service,
        command: str,
    ) -> None:
        result = cli_runner.invoke(cli, [command])
        assert result.exit_code == 2

        state_id = f"pytest_test_{command}"
        args = [command, "--state-id", state_id, tap.name, target.name]

        # exit cleanly when everything is fine
        create_subprocess_exec = AsyncMock(side_effect=(tap_process, target_process))
        with (
            mock.patch.object(SingerTap, "discover_catalog"),
            mock.patch.object(SingerTap, "apply_catalog_rules"),
            mock.patch("meltano.core.plugin_invoker.asyncio") as asyncio_mock,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec

            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            assert_log_lines(
                result.stdout + result.stderr,
                [
                    LogEntry("meltano", None, "Running extract & load...", "info"),
                    LogEntry(
                        None,
                        None,
                        "No state was found, complete import.",
                        "warning",
                    ),
                    LogEntry(
                        None,
                        None,
                        "Incremental state has been updated at",
                        "info",
                    ),
                    LogEntry("meltano", None, "Extract & load complete!", "info"),
                    LogEntry("meltano", None, "Transformation skipped.", "info"),
                ],
            )

            assert_log_lines(
                result.stdout + result.stderr,
                [
                    LogEntry("tap-mock", "extractor", "Starting", "info"),
                    LogEntry("tap-mock", "extractor", "Running", "info"),
                    LogEntry("tap-mock", "extractor", "Done", "info"),
                    LogEntry("target-mock", "loader", "Starting", "info"),
                    LogEntry("target-mock", "loader", "Running", "info"),
                    LogEntry("target-mock", "loader", "Done", "info"),
                ],
            )

        job_logging_service.delete_all_logs(state_id)

        exc = Exception("This is a grave danger.")
        with mock.patch.object(SingerRunner, "run", side_effect=exc):
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert result.exception == exc

            lines = [
                LogEntry("meltano", None, "Running extract & load...", "info"),
                LogEntry(None, None, "This is a grave danger.", "error"),
            ]
            assert_log_lines(result.stderr, lines)
            assert exception_logged(result.stderr, exc)

            # ensure there is a log of this exception
            log = job_logging_service.get_latest_log(state_id).splitlines()
            assert "Traceback (most recent call last):" in log
            assert "Exception: This is a grave danger." in log

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures("use_test_log_config", "project")
    @pytest.mark.parametrize("command", ("elt", "el"), ids=["elt", "el"])
    def test_elt_debug_logging(
        self,
        cli_runner,
        tap,
        target,
        tap_process,
        target_process,
        job_logging_service,
        monkeypatch,
        command: str,
    ) -> None:
        state_id = f"pytest_test_{command}_debug"
        args = [command, "--state-id", state_id, tap.name, target.name]

        job_logging_service.delete_all_logs(state_id)

        create_subprocess_exec = AsyncMock(side_effect=(tap_process, target_process))
        with (
            mock.patch.object(SingerTap, "discover_catalog"),
            mock.patch.object(SingerTap, "apply_catalog_rules"),
            mock.patch("meltano.cli.params.install_plugins"),
            mock.patch(
                "meltano.core.plugin_invoker.asyncio",
            ) as asyncio_mock,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec

            monkeypatch.setenv("MELTANO_CLI_LOG_LEVEL", "debug")
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            lines = [
                LogEntry("meltano", None, "Running extract & load...", "info"),
                LogEntry(
                    None,
                    None,
                    "Created configuration at",
                    "debug",
                ),  # followed by path
                LogEntry(
                    None,
                    None,
                    "Could not find tap.properties.json in",
                    "debug",
                ),  # followed by path
                LogEntry(
                    None,
                    None,
                    "Could not find state.json in",
                    "debug",
                ),  # followed by path
                LogEntry(
                    None,
                    None,
                    "Created configuration at",
                    "debug",
                ),  # followed by path
                LogEntry(None, None, "No state was found, complete import.", "warning"),
                LogEntry(
                    None,
                    None,
                    "Incremental state has been updated at",
                    "info",
                ),  # followed by timestamp
                LogEntry(
                    None,
                    None,
                    "Incremental state: {'line': 1}",
                    "debug",
                ),
                LogEntry(
                    None,
                    None,
                    "Incremental state: {'line': 2}",
                    "debug",
                ),
                LogEntry(
                    None,
                    None,
                    "Incremental state: {'line': 3}",
                    "debug",
                ),
                LogEntry("meltano", None, "Extract & load complete!", "info"),
                LogEntry("meltano", None, "Transformation skipped.", "info"),
                LogEntry("tap-mock", "extractor", "Starting", "info", "stderr"),
                LogEntry("tap-mock", "extractor", "Running", "info", "stderr"),
                LogEntry("tap-mock (out)", "extractor", "SCHEMA", "debug", "stdout"),
                LogEntry("tap-mock (out)", "extractor", "RECORD", "debug", "stdout"),
                LogEntry("tap-mock (out)", "extractor", "STATE", "debug", "stdout"),
                LogEntry("tap-mock", "extractor", "Done", "info", "stderr"),
                LogEntry("target-mock", "loader", "Starting", "info", "stderr"),
                LogEntry("target-mock", "loader", "Running", "info", "stderr"),
                LogEntry(
                    "target-mock (out)",
                    "loader",
                    '{"line": 1}',
                    "debug",
                    "stdout",
                ),
                LogEntry(
                    "target-mock (out)",
                    "loader",
                    '{"line": 2}',
                    "debug",
                    "stdout",
                ),
                LogEntry(
                    "target-mock (out)",
                    "loader",
                    '{"line": 3}',
                    "debug",
                    "stdout",
                ),
                LogEntry("target-mock", "loader", "Done", "info", "stderr"),
            ]

            assert_log_lines(result.stdout + result.stderr, lines)

            log = job_logging_service.get_latest_log(state_id)

            full_result = result.stdout + result.stderr

            # Skip all output lines before 'Running extract & load...' appears.
            # This removes lines emitted by the CLI but not found in the log.
            preserve = False
            cleaned_up_result = []
            for line in full_result.splitlines():
                if "Running extract & load..." in line:
                    preserve = True
                if preserve:
                    cleaned_up_result.append(line)

            message = f"Log contents:\n{full_result}\nCommand output:\n{log}\n"
            assert len(log.splitlines()) == len(cleaned_up_result), message
            # and just to be safe - check if these debug mode only strings show up
            assert "target-mock (out)" in log
            assert "tap-mock (out)" in log

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures("use_test_log_config", "project")
    @pytest.mark.parametrize("command", ("elt", "el"), ids=["elt", "el"])
    def test_elt_tap_failure(
        self,
        cli_runner,
        tap,
        target,
        tap_process,
        target_process,
        job_logging_service,
        command: str,
    ) -> None:
        state_id = f"pytest_test_{command}"
        args = [command, "--state-id", state_id, tap.name, target.name]

        tap_process.wait.return_value = 1
        tap_process.stderr.readline.side_effect = (
            b"Starting\n",
            b"Running\n",
            b"Failure\n",
        )

        invoke_async = AsyncMock(side_effect=(tap_process, target_process))
        with mock.patch.object(
            PluginInvoker,
            "invoke_async",
            new=invoke_async,
        ) as invoke_async:
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert "Extractor failed" in str(result.exception)
            job_logs_file = job_logging_service.get_all_logs(state_id)[0]

            assert_log_lines(
                result.stdout + result.stderr,
                [
                    LogEntry("meltano", None, "Running extract & load...", "info"),
                ],
            )

            assert exception_logged(
                result.stdout + result.stderr,
                CliError(
                    "ELT could not be completed: Extractor failed.\n"
                    + failure_help_log_suffix(job_logs_file),
                ),
            )

            assert_log_lines(
                result.stdout + result.stderr,
                [
                    LogEntry("tap-mock", "extractor", "Starting", "info", "stderr"),
                    LogEntry("tap-mock", "extractor", "Running", "info", "stderr"),
                    LogEntry("tap-mock", "extractor", "Failure", "info", "stderr"),
                    LogEntry("target-mock", "loader", "Starting", "info", "stderr"),
                    LogEntry("target-mock", "loader", "Running", "info", "stderr"),
                    LogEntry("target-mock", "loader", "Done", "info", "stderr"),
                ],
            )

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures("use_test_log_config", "project")
    @pytest.mark.parametrize("command", ("elt", "el"), ids=["elt", "el"])
    def test_elt_target_failure_before_tap_finishes(
        self,
        cli_runner,
        tap,
        target,
        tap_process,
        target_process,
        job_logging_service,
        command: str,
    ) -> None:
        state_id = f"pytest_test_{command}"
        args = [command, "--state-id", state_id, tap.name, target.name]

        # Have `tap_process.wait` take 2s to make sure the target can fail
        # before tap finishes
        async def tap_wait_mock():
            await asyncio.sleep(2)
            return tap_process.wait.return_value

        tap_process.wait.side_effect = tap_wait_mock

        # Writing to target stdin will fail because (we'll pretend) it has already died
        target_process.stdin = mock.Mock(spec=asyncio.StreamWriter)
        target_process.stdin.write.side_effect = BrokenPipeError
        target_process.stdin.drain = AsyncMock(side_effect=ConnectionResetError)
        target_process.stdin.wait_closed = AsyncMock(return_value=True)

        # Have `target_process.wait` take 1s to make sure the
        # `stdin.write`/`drain` exceptions can be raised
        async def target_wait_mock() -> int:
            await asyncio.sleep(1)
            return 1

        target_process.wait.side_effect = target_wait_mock

        target_process.stderr.readline.side_effect = (
            b"Starting\n",
            b"Running\n",
            b"Failure\n",
        )

        invoke_async = AsyncMock(side_effect=(tap_process, target_process))
        with mock.patch.object(
            PluginInvoker,
            "invoke_async",
            new=invoke_async,
        ) as invoke_async:
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert "Loader failed" in str(result.exception)
            job_logs_file = job_logging_service.get_all_logs(state_id)[0]

            assert_log_lines(
                result.stdout + result.stderr,
                [
                    LogEntry("meltano", None, "Running extract & load...", "info"),
                ],
            )
            assert exception_logged(
                result.stdout + result.stderr,
                CliError(
                    "ELT could not be completed: Loader failed.\n"
                    + failure_help_log_suffix(job_logs_file),
                ),
            )

            assert_log_lines(
                result.stdout + result.stderr,
                [
                    LogEntry("tap-mock", "extractor", "Starting", "info", "stderr"),
                    LogEntry("tap-mock", "extractor", "Running", "info", "stderr"),
                    LogEntry("tap-mock", "extractor", "Done", "info", "stderr"),
                    LogEntry("target-mock", "loader", "Starting", "info", "stderr"),
                    LogEntry("target-mock", "loader", "Running", "info", "stderr"),
                    LogEntry("target-mock", "loader", "Failure", "info", "stderr"),
                ],
            )

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures("use_test_log_config", "project")
    @pytest.mark.parametrize("command", ("elt", "el"), ids=["elt", "el"])
    def test_elt_target_failure_after_tap_finishes(
        self,
        cli_runner,
        tap,
        target,
        tap_process,
        target_process,
        job_logging_service,
        command: str,
    ) -> None:
        state_id = f"pytest_test_{command}"
        args = [command, "--state-id", state_id, tap.name, target.name]

        target_process.wait.return_value = 1
        target_process.stderr.readline.side_effect = (
            b"Starting\n",
            b"Running\n",
            b"Failure\n",
        )

        invoke_async = AsyncMock(side_effect=(tap_process, target_process))
        with mock.patch.object(
            PluginInvoker,
            "invoke_async",
            new=invoke_async,
        ) as invoke_async:
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert "Loader failed" in str(result.exception)
            job_logs_file = job_logging_service.get_all_logs(state_id)[0]

            assert_log_lines(
                result.stdout + result.stderr,
                [
                    LogEntry("meltano", None, "Running extract & load...", "info"),
                    LogEntry("meltano", None, "Loading failed", "error"),
                ],
            )
            assert exception_logged(
                result.stdout + result.stderr,
                CliError(
                    "ELT could not be completed: Loader failed.\n"
                    + failure_help_log_suffix(job_logs_file),
                ),
            )

            assert_log_lines(
                result.stdout + result.stderr,
                [
                    LogEntry("tap-mock", "extractor", "Starting", "info", "stderr"),
                    LogEntry("tap-mock", "extractor", "Running", "info", "stderr"),
                    LogEntry("tap-mock", "extractor", "Done", "info", "stderr"),
                    LogEntry("target-mock", "loader", "Starting", "info", "stderr"),
                    LogEntry("target-mock", "loader", "Running", "info", "stderr"),
                    LogEntry("target-mock", "loader", "Failure", "info", "stderr"),
                ],
            )

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures("use_test_log_config", "project")
    @pytest.mark.parametrize("command", ("elt", "el"), ids=["elt", "el"])
    def test_elt_tap_and_target_failure(
        self,
        cli_runner,
        tap,
        target,
        tap_process,
        target_process,
        job_logging_service,
        command: str,
    ) -> None:
        state_id = f"pytest_test_{command}"
        args = [command, "--state-id", state_id, tap.name, target.name]

        tap_process.wait.return_value = 1
        tap_process.stderr.readline.side_effect = (
            b"Starting\n",
            b"Running\n",
            b"Failure\n",
        )

        target_process.wait.return_value = 1
        target_process.stderr.readline.side_effect = (
            b"Starting\n",
            b"Running\n",
            b"Failure\n",
        )

        invoke_async = AsyncMock(side_effect=(tap_process, target_process))
        with mock.patch.object(
            PluginInvoker,
            "invoke_async",
            new=invoke_async,
        ) as invoke_async:
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert "Extractor and loader failed" in str(result.exception)
            job_logs_file = job_logging_service.get_all_logs(state_id)[0]

            assert_log_lines(
                result.stdout + result.stderr,
                [
                    LogEntry("meltano", None, "Running extract & load...", "info"),
                    LogEntry("meltano", None, "Extraction failed", "error"),
                    LogEntry("meltano", None, "Loading failed", "error"),
                ],
            )

            assert exception_logged(
                result.stdout + result.stderr,
                CliError(
                    "ELT could not be completed: Extractor and loader failed.\n"
                    + failure_help_log_suffix(job_logs_file),
                ),
            )

            assert_log_lines(
                result.stdout + result.stderr,
                [
                    LogEntry("tap-mock", "extractor", "Starting", "info", "stderr"),
                    LogEntry("tap-mock", "extractor", "Running", "info", "stderr"),
                    LogEntry("tap-mock", "extractor", "Failure", "info", "stderr"),
                    LogEntry("target-mock", "loader", "Starting", "info", "stderr"),
                    LogEntry("target-mock", "loader", "Running", "info", "stderr"),
                    LogEntry("target-mock", "loader", "Failure", "info", "stderr"),
                ],
            )

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures("use_test_log_config", "project")
    @pytest.mark.parametrize("command", ("elt", "el"), ids=["elt", "el"])
    def test_elt_tap_line_length_limit_error(
        self,
        cli_runner,
        tap,
        target,
        tap_process,
        target_process,
        job_logging_service,
        command: str,
    ) -> None:
        state_id = f"pytest_test_{command}"
        args = [command, "--state-id", state_id, tap.name, target.name]

        # Raise a `ValueError` wrapping a `LimitOverrunError`, like
        # `StreamReader.readline` does:
        # https://github.com/python/cpython/blob/v3.8.7/Lib/asyncio/streams.py#L549
        try:
            raise asyncio.LimitOverrunError(  # noqa: TRY003, TRY301
                "Separator is not found, and chunk exceed the limit",  # noqa: EM101
                0,
            )
        except asyncio.LimitOverrunError as err:
            try:
                # `ValueError` needs to be raised from inside the except block
                # for `LimitOverrunError` so that `__context__` is set.
                raise ValueError(str(err))  # noqa: TRY301
            except ValueError as wrapper_err:
                tap_process.stdout.readline.side_effect = wrapper_err

        # Have `tap_process.wait` take 1s to make sure the `LimitOverrunError`
        # exception can be raised before tap finishes
        async def wait_mock():
            await asyncio.sleep(1)
            return tap_process.wait.return_value

        tap_process.wait.side_effect = wait_mock

        invoke_async = AsyncMock(side_effect=(tap_process, target_process))
        with mock.patch.object(
            PluginInvoker,
            "invoke_async",
            new=invoke_async,
        ) as invoke_async:
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert "Output line length limit exceeded" in str(result.exception)
            job_logs_file = job_logging_service.get_all_logs(state_id)[0]

            assert_log_lines(
                result.stdout + result.stderr,
                [
                    LogEntry("meltano", None, "Running extract & load...", "info"),
                    LogEntry(
                        None,
                        None,
                        (
                            "The extractor generated a message exceeding the "
                            "message size limit of 50.0MiB (half the buffer "
                            "size of 100.0MiB)."
                        ),
                        "error",
                    ),
                ],
            )

            assert exception_logged(
                result.stdout + result.stderr,
                CliError(
                    "ELT could not be completed: Output line length limit exceeded.\n"
                    + failure_help_log_suffix(job_logs_file),
                ),
            )

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures("use_test_log_config", "project")
    @pytest.mark.parametrize("command", ("elt", "el"), ids=["elt", "el"])
    def test_elt_output_handler_error(
        self,
        cli_runner,
        tap,
        target,
        tap_process,
        target_process,
        command: str,
    ) -> None:
        state_id = f"pytest_test_{command}"
        args = [command, "--state-id", state_id, tap.name, target.name]

        exc = Exception("Failed to read from target stderr.")
        target_process.stderr.readline.side_effect = exc

        # Have `tap_process.wait` take 1s to make sure the exception can be
        # raised before tap finishes
        async def wait_mock():
            await asyncio.sleep(1)
            return tap_process.wait.return_value

        tap_process.wait.side_effect = wait_mock

        invoke_async = AsyncMock(side_effect=(tap_process, target_process))
        with mock.patch.object(
            PluginInvoker,
            "invoke_async",
            new=invoke_async,
        ) as invoke_async:
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert result.exception == exc

            assert_log_lines(
                result.stderr,
                [
                    LogEntry("meltano", None, "Running extract & load...", "info"),
                ],
            )

            assert exception_logged(
                result.stderr,
                Exception("Failed to read from target stderr."),
            )

    @pytest.mark.parametrize("command", ("elt", "el"), ids=["elt", "el"])
    def test_elt_already_running(
        self,
        cli_runner,
        tap,
        target,
        session,
        command: str,
    ) -> None:
        state_id = "already_running"
        args = [command, "--state-id", state_id, tap.name, target.name]

        existing_job = Job(job_name=state_id, state=State.RUNNING)
        existing_job.save(session)

        with mock.patch(
            "meltano.cli.elt.project_engine",
            return_value=(None, lambda: session),
        ):
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert f"Another '{state_id}' pipeline is already running" in str(
                result.exception,
            )

    @pytest.mark.parametrize("command", ("elt", "el"), ids=["elt", "el"])
    def test_dump_catalog(
        self,
        cli_runner,
        project,
        tap,
        target,
        command: str,
    ) -> None:
        catalog = {"streams": []}
        with project.root.joinpath("catalog.json").open("w") as catalog_file:
            json.dump(catalog, catalog_file)

        state_id = f"pytest_test_{command}"
        args = [
            command,
            "--state-id",
            state_id,
            tap.name,
            target.name,
            "--catalog",
            "catalog.json",
            "--dump",
            "catalog",
        ]

        result = cli_runner.invoke(cli, args)
        assert_cli_runner(result)

        assert json.loads(result.stdout) == catalog

    @pytest.mark.usefixtures("session")
    @pytest.mark.parametrize("command", ("elt", "el"), ids=["elt", "el"])
    def test_dump_state(
        self,
        cli_runner,
        project,
        tap,
        target,
        command: str,
    ) -> None:
        state = {"success": True}
        with project.root.joinpath("state.json").open("w") as state_file:
            json.dump(state, state_file)

        state_id = f"pytest_test_{command}"
        args = [
            command,
            "--state-id",
            state_id,
            tap.name,
            target.name,
            "--state",
            "state.json",
            "--dump",
            "state",
        ]

        with (
            mock.patch.object(SingerTap, "discover_catalog"),
            mock.patch.object(SingerTap, "apply_catalog_rules"),
        ):
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            assert json.loads(result.stdout) == state

    @pytest.mark.usefixtures("project")
    @pytest.mark.parametrize("command", ("elt", "el"), ids=["elt", "el"])
    def test_dump_extractor_config(
        self,
        cli_runner,
        tap,
        target,
        plugin_settings_service_factory,
        command: str,
    ) -> None:
        state_id = f"pytest_test_{command}"
        args = [
            command,
            "--state-id",
            state_id,
            tap.name,
            target.name,
            "--dump",
            "extractor-config",
        ]

        settings_service = plugin_settings_service_factory(tap)

        with (
            mock.patch.object(SingerTap, "discover_catalog"),
            mock.patch.object(SingerTap, "apply_catalog_rules"),
        ):
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            assert json.loads(result.stdout) == settings_service.as_dict(
                extras=False,
                process=True,
            )

    @pytest.mark.usefixtures("project")
    @pytest.mark.parametrize("command", ("elt", "el"), ids=["elt", "el"])
    def test_dump_loader_config(
        self,
        cli_runner,
        tap,
        target,
        plugin_settings_service_factory,
        command: str,
    ) -> None:
        state_id = f"pytest_test_{command}"
        args = [
            command,
            "--state-id",
            state_id,
            tap.name,
            target.name,
            "--dump",
            "loader-config",
        ]

        settings_service = plugin_settings_service_factory(target)

        with (
            mock.patch.object(SingerTap, "discover_catalog"),
            mock.patch.object(SingerTap, "apply_catalog_rules"),
        ):
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            assert json.loads(result.stdout) == settings_service.as_dict(
                extras=False,
                process=True,
            )


@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="ELT is not supported on Windows",
)
class TestCliEltScratchpadTwo:
    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "dbt",
        "tap_mock_transform",
    )
    def test_elt_transform_run(
        self,
        cli_runner,
        tap,
        target,
        tap_process,
        target_process,
        silent_dbt_process,
        dbt_process,
    ) -> None:
        args = ["elt", tap.name, target.name, "--transform", "run"]

        invoke_async = AsyncMock(
            side_effect=(
                tap_process,
                target_process,
                silent_dbt_process,  # dbt clean
                silent_dbt_process,  # dbt deps
                dbt_process,  # dbt run
            ),
        )
        with mock.patch.object(
            PluginInvoker,
            "invoke_async",
            new=invoke_async,
        ) as invoke_async:
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            assert_log_lines(
                result.stdout + result.stderr,
                [
                    LogEntry("meltano", None, "Running extract & load...", "info"),
                    LogEntry("meltano", None, "Extract & load complete!", "info"),
                    LogEntry("meltano", None, "Running transformation...", "info"),
                    LogEntry("meltano", None, "Transformation complete!", "info"),
                ],
            )

            assert_log_lines(
                result.stdout + result.stderr,
                [
                    LogEntry("tap-mock", "extractor", "Starting", "info"),
                    LogEntry("tap-mock", "extractor", "Running", "info"),
                    LogEntry("tap-mock", "extractor", "Done", "info"),
                    LogEntry("target-mock", "loader", "Starting", "info"),
                    LogEntry("target-mock", "loader", "Running", "info"),
                    LogEntry("target-mock", "loader", "Done", "info"),
                    LogEntry("dbt", "transformer", "Starting", "info"),
                    LogEntry("dbt", "transformer", "Running", "info"),
                    LogEntry("dbt", "transformer", "Done", "info"),
                ],
            )

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "dbt",
        "tap_mock_transform",
    )
    def test_elt_transform_run_dbt_failure(
        self,
        cli_runner: MeltanoCliRunner,
        tap,
        target,
        tap_process,
        target_process,
        silent_dbt_process,
        dbt_process,
        job_logging_service,
    ) -> None:
        state_id = "pytest_test_elt"
        args = [
            "elt",
            "--state-id",
            state_id,
            tap.name,
            target.name,
            "--transform",
            "run",
        ]

        dbt_process.wait.return_value = 1
        dbt_process.returncode = 1
        dbt_process.stderr.readline.side_effect = (
            b"Starting\n",
            b"Running\n",
            b"Failure\n",
        )

        invoke_async = AsyncMock(
            side_effect=(
                tap_process,
                target_process,
                silent_dbt_process,  # dbt clean
                silent_dbt_process,  # dbt deps
                dbt_process,  # dbt run
            ),
        )
        with mock.patch.object(
            PluginInvoker,
            "invoke_async",
            new=invoke_async,
        ) as invoke_async:
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert "`dbt run` failed" in str(result.exception)
            job_logs_file = job_logging_service.get_all_logs(state_id)[0]

            assert_log_lines(
                result.stdout + result.stderr,
                [
                    LogEntry("meltano", None, "Running extract & load...", "info"),
                    LogEntry("meltano", None, "Extract & load complete!", "info"),
                    LogEntry("meltano", None, "Running transformation...", "info"),
                    LogEntry("meltano", None, "Transformation failed", "error"),
                ],
            )
            assert isinstance(result.exception, CliError)
            message = (
                "ELT could not be completed: `dbt run` failed.\n"
                f"{failure_help_log_suffix(job_logs_file)}"
            )
            assert message in str(result.exception)

            assert_log_lines(
                result.stdout + result.stderr,
                [
                    LogEntry("tap-mock", "extractor", "Starting", "info"),
                    LogEntry("tap-mock", "extractor", "Running", "info"),
                    LogEntry("tap-mock", "extractor", "Done", "info"),
                    LogEntry("target-mock", "loader", "Starting", "info"),
                    LogEntry("target-mock", "loader", "Running", "info"),
                    LogEntry("target-mock", "loader", "Done", "info"),
                    LogEntry("dbt", "transformer", "Starting", "info"),
                    LogEntry("dbt", "transformer", "Running", "info"),
                    LogEntry("dbt", "transformer", "Failure", "info"),
                ],
            )


@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="ELT is not supported on Windows",
)
class TestCliEltScratchpadThree:
    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures("use_test_log_config", "project", "dbt")
    def test_elt_transform_only(
        self,
        cli_runner,
        tap,
        target,
    ) -> None:
        args = ["elt", tap.name, target.name, "--transform", "only"]

        with mock.patch.object(DbtRunner, "run", new=AsyncMock()):
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            assert_log_lines(
                result.stdout + result.stderr,
                [
                    LogEntry(
                        None,
                        None,
                        "The `elt` command is deprecated in favor of `el`",
                        "warning",
                    ),
                    LogEntry("meltano", None, "Extract & load skipped.", "info"),
                    LogEntry("meltano", None, "Running transformation...", "info"),
                    LogEntry("meltano", None, "Transformation complete!", "info"),
                ],
            )

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "dbt",
        "tap_mock_transform",
    )
    def test_elt_transform_only_with_transform(
        self,
        cli_runner,
        tap,
        target,
    ) -> None:
        args = ["elt", tap.name, target.name, "--transform", "only"]

        with mock.patch.object(DbtRunner, "run", new=AsyncMock()):
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)
            assert_log_lines(
                result.stdout + result.stderr,
                [
                    LogEntry("meltano", None, "Extract & load skipped.", "info"),
                    LogEntry("meltano", None, "Running transformation...", "info"),
                    LogEntry("meltano", None, "Transformation complete!", "info"),
                ],
            )
