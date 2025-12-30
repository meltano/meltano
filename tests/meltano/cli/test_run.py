from __future__ import annotations

import asyncio
import json
import re
import typing as t
from unittest import mock
from unittest.mock import AsyncMock

import pytest

from meltano.cli import cli
from meltano.core.block.ioblock import IOBlock
from meltano.core.logging.job_logging_service import MissingJobLogException
from meltano.core.logging.utils import default_config
from meltano.core.plugin import PluginType
from meltano.core.plugin.singer import SingerTap
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.project_plugins_service import (
    AmbiguousMappingName,
    PluginAlreadyAddedException,
)

if t.TYPE_CHECKING:
    from fixtures.cli import MeltanoCliRunner
    from meltano.core.logging.job_logging_service import JobLoggingService
    from meltano.core.project import Project


class MockIOBlock(IOBlock):
    string_id = "mock-io-block"


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
        side_effect=(b"tap starting\n", b"tap running\n", b"tap done\n"),
    )
    return tap


@pytest.fixture
def target_process(process_mock_factory, target):
    target = process_mock_factory(target)

    # Have `target.wait` take 2s to make sure the tap always finishes before the target
    async def wait_mock():
        await asyncio.sleep(2)
        return target.wait.return_value

    target.wait.side_effect = wait_mock

    target.stdout.at_eof.side_effect = (False, False, False, True)
    target.stdout.readline = AsyncMock(
        side_effect=(b'{"line": 1}\n', b'{"line": 2}\n', b'{"line": 3}\n'),
    )
    target.stderr.at_eof.side_effect = (False, False, False, True)
    target.stderr.readline = AsyncMock(
        side_effect=(b"target starting\n", b"target running\n", b"target done\n"),
    )
    return target


@pytest.fixture
def mapper_process(process_mock_factory, mapper):
    mapper = process_mock_factory(mapper)

    # Have `mapper.wait` take 1s to make sure the mapper always finishes after
    # the tap but before the target
    async def wait_mock():
        await asyncio.sleep(1)
        return mapper.wait.return_value

    mapper.wait.side_effect = wait_mock

    mapper.stdout.at_eof.side_effect = (False, False, False, True)
    mapper.stdout.readline = AsyncMock(
        side_effect=(b"SCHEMA\n", b"RECORD\n", b"STATE\n"),
    )
    mapper.stderr.at_eof.side_effect = (False, False, False, True)
    mapper.stderr.readline = AsyncMock(
        side_effect=(b"mapper starting\n", b"mapper running\n", b"mapper done\n"),
    )
    return mapper


@pytest.fixture
def dbt_process(process_mock_factory, dbt):
    dbt = process_mock_factory(dbt)

    async def wait_mock():
        await asyncio.sleep(1)
        return dbt.wait.return_value

    dbt.wait.side_effect = wait_mock

    dbt.stdout.at_eof.side_effect = (False, True)
    dbt.stdout.readline = AsyncMock(side_effect=(b"Testoutput"))
    dbt.stderr.at_eof.side_effect = (False, False, False, True)
    dbt.stderr.readline = AsyncMock(
        side_effect=(b"dbt starting\n", b"dbt running\n", b"dbt done\n"),
    )
    return dbt


class EventMatcher:
    def __init__(self, result_output: str):
        """Build a matcher for the result output of a command."""
        self.seen_events: list[dict] = []
        self.seen_raw: list[str] = []

        for line in result_output.splitlines():
            try:
                parsed_line = json.loads(line)
            except json.JSONDecodeError:  # pragma: no cover
                self.seen_raw.append(line)
                continue
            self.seen_events.append(parsed_line)

    def event_matches(self, event: str) -> bool:
        """Search result output for an event, that matches the given event.

        Args:
            event: the event to search for.

        Returns:
            True if the event was found, False otherwise.
        """
        for line in self.seen_events:
            matches = line["event"] == event
            if matches:
                return True

        return False

    def find_by_event(self, event: str) -> list[dict]:
        """Return the first matching event, that matches the given event.

        Args:
            event: the event to search for.

        Returns:
            A list of matching events.
        """
        matches = []
        for line in self.seen_events:
            match = line["event"] == event
            if match:
                matches.append(line)
        return matches

    def find_first_event(self, event: str) -> dict | None:
        """Return the first matching event, that matches the given event.

        Args:
            event: the event to search for.
        """
        return next((line for line in self.seen_events if line["event"] == event), None)


class TestCliRunScratchpadOne:
    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures("use_test_log_config", "project", "job_logging_service")
    def test_run_parsing_failures(
        self,
        cli_runner,
        tap,
        target,
        tap_process,
        target_process,
    ) -> None:
        result = cli_runner.invoke(cli, ["run"])
        assert result.exit_code == 0

        assert EventMatcher(result.stderr).event_matches("No valid blocks found.")

        args = ["run", tap.name]

        # exit cleanly when everything is fine
        create_subprocess_exec = AsyncMock(side_effect=(tap_process, target_process))

        # check that the various ELB validation checks actually run and fail as expected
        with (
            mock.patch.object(SingerTap, "discover_catalog"),
            mock.patch.object(SingerTap, "apply_catalog_rules"),
            mock.patch("meltano.core.plugin_invoker.asyncio") as asyncio_mock,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec
            with pytest.raises(Exception, match="Loader missing in block set!"):
                cli_runner.invoke(cli, args, catch_exceptions=False)

        args = ["run", tap.name, tap.name, target.name]
        with (
            mock.patch.object(SingerTap, "discover_catalog"),
            mock.patch.object(SingerTap, "apply_catalog_rules"),
            mock.patch("meltano.core.plugin_invoker.asyncio") as asyncio_mock2,
        ):
            asyncio_mock2.create_subprocess_exec = create_subprocess_exec
            with pytest.raises(
                Exception,
                match=(
                    "Unknown command type or bad block sequence at index 1, "
                    "starting block 'tap-mock'"
                ),
            ):
                cli_runner.invoke(cli, args, catch_exceptions=False)

        args = ["run", tap.name, target.name, target.name]
        with (
            mock.patch.object(SingerTap, "discover_catalog"),
            mock.patch.object(SingerTap, "apply_catalog_rules"),
            mock.patch("meltano.core.plugin_invoker.asyncio") as asyncio_mock3,
        ):
            asyncio_mock3.create_subprocess_exec = create_subprocess_exec
            with pytest.raises(
                Exception,
                match=(
                    "Unknown command type or bad block sequence at index 3, "
                    "starting block 'target-mock'"
                ),
            ):
                cli_runner.invoke(cli, args, catch_exceptions=False)

        # Verify that a vanilla ELB run works
        args = ["run", tap.name, target.name]
        with (
            mock.patch.object(SingerTap, "discover_catalog"),
            mock.patch.object(SingerTap, "apply_catalog_rules"),
            mock.patch("meltano.core.plugin_invoker.asyncio") as asyncio_mock4,
        ):
            asyncio_mock4.create_subprocess_exec = create_subprocess_exec
            result = cli_runner.invoke(cli, args, catch_exceptions=False)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)

            assert matcher.event_matches(
                "All ExtractLoadBlocks validated, starting execution.",
            )
            completion_event = matcher.find_by_event("Block run completed")[0]
            assert completion_event["success"]
            assert completion_event["duration_seconds"] > 0

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "mapper",
        "dbt",
        "job_logging_service",
    )
    def test_run_basic_invocations(
        self,
        cli_runner,
        tap,
        target,
        tap_process,
        target_process,
        mapper_process,
        dbt_process,
    ) -> None:
        # exit cleanly when everything is fine
        create_subprocess_exec = AsyncMock(
            side_effect=(tap_process, mapper_process, target_process),
        )

        # Verify that a vanilla ELB run works
        args = ["run", tap.name, "mock-mapping-0", target.name]
        with (
            mock.patch.object(SingerTap, "discover_catalog"),
            mock.patch.object(SingerTap, "apply_catalog_rules"),
            mock.patch("meltano.core.plugin_invoker.asyncio") as asyncio_mock,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec
            result = cli_runner.invoke(cli, args, catch_exceptions=True)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)

            assert matcher.event_matches(
                "All ExtractLoadBlocks validated, starting execution.",
            )
            target_stop_event = matcher.find_by_event("target done")
            assert len(target_stop_event) == 1
            assert target_stop_event[0]["name"] == target.name
            assert target_stop_event[0]["cmd_type"] == "elb"
            assert target_stop_event[0]["stdio"] == "stderr"

            events = matcher.find_by_event("Block run completed")
            assert len(events) == 1
            completion_event = events[0]
            assert completion_event["success"]
            assert completion_event["duration_seconds"] > 0

        # Verify that a vanilla command plugin (dbt:run) run works
        invoke_async = AsyncMock(side_effect=(dbt_process,))  # dbt run
        args = ["run", "dbt:run"]
        with mock.patch.object(PluginInvoker, "invoke_async", new=invoke_async):
            result = cli_runner.invoke(cli, args, catch_exceptions=False)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)
            events = matcher.find_first_event("found plugin in cli invocation")
            assert events is not None
            assert events.get("plugin_name") == "dbt"

            dbt_start_event = matcher.find_first_event("dbt done")
            assert dbt_start_event is not None
            assert dbt_start_event["name"] == "dbt"
            assert dbt_start_event["cmd_type"] == "command"
            assert dbt_start_event["stdio"] == "stderr"

            completion_event = matcher.find_first_event("Block run completed")
            assert completion_event is not None
            assert completion_event["success"]
            assert completion_event["duration_seconds"] > 0

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures("use_test_log_config", "project")
    def test_run_custom_suffix_command_option(
        self,
        cli_runner,
        tap,
        target,
        tap_process,
        target_process,
        job_logging_service: JobLoggingService,
    ) -> None:
        # exit cleanly when everything is fine
        create_subprocess_exec = AsyncMock(side_effect=(tap_process, target_process))

        # Verify that a state ID with custom suffix from command option is
        # generated for an ELB run
        args = ["run", tap.name, target.name, "--state-id-suffix", "test-suffix"]

        with (
            mock.patch.object(SingerTap, "discover_catalog"),
            mock.patch.object(SingerTap, "apply_catalog_rules"),
            mock.patch("meltano.core.plugin_invoker.asyncio") as asyncio_mock,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec
            result = cli_runner.invoke(cli, args, catch_exceptions=True)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)
            completion_event = matcher.find_first_event("Block run completed")
            assert completion_event is not None
            assert completion_event["success"]
            assert completion_event["duration_seconds"] > 0

            job_logging_service.get_latest_log(
                f"dev:{tap.name}-to-{target.name}:test-suffix",
            )

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures("use_test_log_config")
    @pytest.mark.parametrize(
        "suffix_args",
        (
            (
                "test-suffix",
                "test-suffix",
                [],
            ),
            (
                "${TEST_SUFFIX}",
                "test-suffix-single-env",
                [
                    ("TEST_SUFFIX", "test-suffix-single-env"),
                ],
            ),
            (
                "test-suffix-${TEST_SUFFIX_0}-${TEST_SUFFIX_1}",
                "test-suffix-multiple-env",
                [
                    ("TEST_SUFFIX_0", "multiple"),
                    ("TEST_SUFFIX_1", "env"),
                ],
            ),
        ),
        ids=[
            "static",
            "dynamic (single env)",
            "dynamic (multiple env)",
        ],
    )
    def test_run_custom_suffix_active_environment(
        self,
        suffix_args,
        cli_runner,
        project: Project,
        tap,
        target,
        tap_process,
        target_process,
        job_logging_service: JobLoggingService,
    ) -> None:
        state_id_suffix, expected_suffix, suffix_env = suffix_args

        # exit cleanly when everything is fine
        create_subprocess_exec = AsyncMock(side_effect=(tap_process, target_process))

        # Verify that a state ID with custom suffix from active environment is
        # generated for an ELB run
        project.activate_environment("dev")

        assert project.environment is not None
        project.environment.state_id_suffix = state_id_suffix

        args = ["run", tap.name, target.name]

        with (
            mock.patch.object(SingerTap, "discover_catalog"),
            mock.patch.object(SingerTap, "apply_catalog_rules"),
            mock.patch(
                "meltano.core.plugin_invoker.asyncio",
            ) as asyncio_mock,
            pytest.MonkeyPatch().context() as mp,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec

            for env in suffix_env:
                mp.setenv(*env)

            result = cli_runner.invoke(cli, args, catch_exceptions=True)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)
            completion_event = matcher.find_first_event("Block run completed")
            assert completion_event is not None
            assert completion_event["success"]
            assert completion_event["duration_seconds"] > 0

            job_logging_service.get_latest_log(
                f"dev:{tap.name}-to-{target.name}:${expected_suffix}",
            )

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures("use_test_log_config")
    def test_run_no_state_update(
        self,
        cli_runner,
        tap,
        target,
        tap_process,
        target_process,
        job_logging_service: JobLoggingService,
        worker_id: str,
    ):
        # exit cleanly when everything is fine
        create_subprocess_exec = AsyncMock(side_effect=(tap_process, target_process))

        # Verify that no logs are created when `--no-state-update` is passed
        args = [
            "run",
            tap.name,
            target.name,
            "--no-state-update",
            "--state-id-suffix",
            worker_id,
        ]
        state_id = f"dev:{tap.name}-to-{target.name}:{worker_id}"

        with (
            mock.patch.object(SingerTap, "discover_catalog"),
            mock.patch.object(SingerTap, "apply_catalog_rules"),
            mock.patch("meltano.core.plugin_invoker.asyncio") as asyncio_mock,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec
            result = cli_runner.invoke(cli, args, catch_exceptions=True)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)
            completion_event = matcher.find_first_event("Block run completed")
            assert completion_event is not None
            assert completion_event["success"]
            assert completion_event["duration_seconds"] > 0

            with pytest.raises(MissingJobLogException):
                job_logging_service.get_latest_log(state_id)

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "dbt",
        "job_logging_service",
    )
    def test_run_multiple_commands(self, cli_runner, dbt_process) -> None:
        # Verify that requesting the same command plugin multiple time with
        # different args works
        invoke_async = AsyncMock(
            side_effect=(
                dbt_process,
                dbt_process,
            ),
        )
        args = ["run", "dbt:test", "dbt:run"]
        with mock.patch.object(PluginInvoker, "invoke_async", new=invoke_async):
            result = cli_runner.invoke(cli, args, catch_exceptions=False)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)
            event = matcher.find_first_event("found plugin in cli invocation")
            assert event is not None
            assert event.get("plugin_name") == "dbt"

            command_add_events = matcher.find_by_event(
                "plugin command added for execution",
            )
            assert len(command_add_events) == 2
            assert invoke_async.call_count == 2

            assert command_add_events[0]["command_name"] == "test"
            assert invoke_async.mock_calls[0][2]["command"] == "test"

            assert command_add_events[1]["command_name"] == "run"
            assert invoke_async.mock_calls[1][2]["command"] == "run"

            completion_events = matcher.find_by_event("Block run completed")
            assert len(completion_events) == 2
            assert completion_events[0]["success"]
            assert completion_events[0]["duration_seconds"] > 0
            assert completion_events[1]["success"]
            assert completion_events[1]["duration_seconds"] > 0

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "mapper",
        "dbt",
        "job_logging_service",
    )
    def test_run_complex_invocations(
        self,
        cli_runner,
        tap,
        target,
        tap_process,
        target_process,
        mapper_process,
        dbt_process,
    ) -> None:
        invoke_async = AsyncMock(
            side_effect=(tap_process, mapper_process, target_process, dbt_process),
        )
        args = ["run", tap.name, "mock-mapping-0", target.name, "dbt:run"]
        with mock.patch.object(PluginInvoker, "invoke_async", new=invoke_async):
            result = cli_runner.invoke(cli, args, catch_exceptions=False)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)
            assert matcher.event_matches(
                "found ExtractLoadBlocks set",
            )  # tap/target pair

            # make sure mapper was found and at its expected positions
            for ev in matcher.find_by_event("found block"):
                if ev["block_type"] == "mappers":
                    assert ev["index"] == 1

            assert (
                matcher.find_by_event("found PluginCommand")[0]["plugin_type"]
                == "transformers"
            )  # dbt

            completed_events = matcher.find_by_event("Block run completed")
            assert len(completed_events) == 2
            for event in completed_events:
                assert event["success"]
                assert event["duration_seconds"] > 0

            tap_stop_event = matcher.find_by_event("tap done")
            assert len(tap_stop_event) == 1
            assert tap_stop_event[0]["name"] == tap.name
            assert tap_stop_event[0]["cmd_type"] == "elb"
            assert tap_stop_event[0]["stdio"] == "stderr"

            target_stop_event = matcher.find_by_event("target done")
            assert len(target_stop_event) == 1
            assert target_stop_event[0]["name"] == target.name
            assert target_stop_event[0]["cmd_type"] == "elb"
            assert target_stop_event[0]["stdio"] == "stderr"

            dbt_done_event = matcher.find_by_event("dbt done")
            assert len(dbt_done_event) == 1
            assert dbt_done_event[0]["name"] == "dbt"
            assert dbt_done_event[0]["cmd_type"] == "command"
            assert dbt_done_event[0]["stdio"] == "stderr"

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "dbt",
        "job_logging_service",
    )
    def test_run_plugin_command_failure(
        self,
        cli_runner,
        tap,
        target,
        tap_process,
        target_process,
        dbt_process,
    ) -> None:
        args = ["run", tap.name, target.name, "dbt:run"]

        dbt_process.wait.return_value = 1
        dbt_process.returncode = 1
        dbt_process.stderr.readline.side_effect = (
            b"dbt starting\n",
            b"dbt running\n",
            b"dbt failure\n",
        )

        invoke_async = AsyncMock(side_effect=(tap_process, target_process, dbt_process))

        with mock.patch.object(PluginInvoker, "invoke_async", new=invoke_async):
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert "`dbt run` failed" in result.output

            matcher = EventMatcher(result.stderr)
            assert matcher.event_matches(
                "found ExtractLoadBlocks set",
            )  # tap/target pair
            assert (
                matcher.find_by_event("found PluginCommand")[0]["plugin_type"]
                == "transformers"
            )  # dbt

            completed_events = matcher.find_by_event("Block run completed")
            assert len(completed_events) == 2
            for event in completed_events:
                if event["block_type"] == "ExtractLoadBlocks":
                    assert event["success"]
                    assert event["duration_seconds"] > 0
                elif event["block_type"] == "InvokerCommand":
                    assert event["success"] is False
                    assert event["duration_seconds"] > 0

            tap_stop_event = matcher.find_by_event("tap done")
            assert len(tap_stop_event) == 1
            assert tap_stop_event[0]["name"] == tap.name
            assert tap_stop_event[0]["cmd_type"] == "elb"
            assert tap_stop_event[0]["stdio"] == "stderr"

            target_stop_event = matcher.find_by_event("target done")
            assert len(target_stop_event) == 1
            assert target_stop_event[0]["name"] == target.name
            assert target_stop_event[0]["cmd_type"] == "elb"
            assert target_stop_event[0]["stdio"] == "stderr"

            assert not matcher.event_matches("dbt done")
            assert matcher.event_matches("dbt starting")
            assert matcher.event_matches("dbt running")
            assert matcher.event_matches("dbt failure")

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "dbt",
        "job_logging_service",
    )
    def test_run_elb_tap_failure(
        self,
        cli_runner,
        tap,
        target,
        tap_process,
        target_process,
        dbt_process,
    ) -> None:
        # In this scenario, the tap fails on the third read. Target should still
        # complete, but dbt should not.
        args = ["run", tap.name, target.name, "dbt:run"]

        tap_process.wait.return_value = 1
        tap_process.returncode = 1
        tap_process.stderr.readline.side_effect = (
            b"tap starting\n",
            b"tap running\n",
            b"tap failure\n",
        )

        invoke_async = AsyncMock(side_effect=(tap_process, target_process, dbt_process))

        with mock.patch.object(PluginInvoker, "invoke_async", new=invoke_async):
            result = cli_runner.invoke(cli, args)

            assert "Extractor failed" in result.output
            assert result.exit_code == 1

            matcher = EventMatcher(result.stderr)
            assert matcher.event_matches("found ExtractLoadBlocks set")
            assert (
                matcher.find_by_event("found PluginCommand")[0]["plugin_type"]
                == "transformers"
            )

            completed_events = matcher.find_by_event("Block run completed")
            assert len(completed_events) == 1
            assert completed_events[0]["success"] is False
            assert completed_events[0]["duration_seconds"] > 0

            assert completed_events[0]["err"] == "Extractor failed"
            assert completed_events[0]["exit_codes"]["extractors"] == 1

            tap_stop_event = matcher.find_by_event("tap failure")
            assert len(tap_stop_event) == 1
            assert tap_stop_event[0]["name"] == tap.name
            assert tap_stop_event[0]["cmd_type"] == "elb"
            assert tap_stop_event[0]["stdio"] == "stderr"

            target_stop_event = matcher.find_by_event("target done")
            assert len(target_stop_event) == 1
            assert target_stop_event[0]["name"] == target.name
            assert target_stop_event[0]["cmd_type"] == "elb"
            assert target_stop_event[0]["stdio"] == "stderr"

            # dbt should not have run at all
            assert not matcher.event_matches("dbt starting")
            assert not matcher.event_matches("dbt running")
            assert not matcher.event_matches("dbt done")

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "dbt",
        "job_logging_service",
    )
    def test_run_elb_target_failure_before_tap_finished(
        self,
        cli_runner,
        tap,
        target,
        tap_process,
        target_process,
        dbt_process,
    ) -> None:
        args = ["run", tap.name, target.name, "dbt:run"]

        # Have `tap_process.wait` take 2s to make sure the target can fail
        # before tap finishes
        async def tap_wait_mock():
            await asyncio.sleep(2)
            return tap_process.wait.return_value

        tap_process.wait.side_effect = tap_wait_mock

        # Writing to target stdin will fail because (we'll pretend) it has already died
        target_process.stdin = mock.Mock(spec=asyncio.StreamWriter)
        # capture_subprocess_output writer will return and close the pipe when
        # either BrokenPipeError or ConnectionResetError is enccountered it
        # does not itself reraise the exception - so you shouldn't expect to see these.
        target_process.stdin.write.side_effect = BrokenPipeError
        target_process.stdin.drain = AsyncMock(side_effect=ConnectionResetError)
        target_process.stdin.wait_closed = AsyncMock(return_value=True)

        # Have `target_process.wait` take 1s to make sure the
        # `stdin.write`/`drain` exceptions can be raised
        async def target_wait_mock() -> int:
            await asyncio.sleep(1)
            return 1

        target_process.wait.side_effect = target_wait_mock

        target_process.wait.return_value = 1
        target_process.returncode = 1
        target_process.stderr.readline.side_effect = (
            b"target starting\n",
            b"target running\n",
            b"target failure\n",
        )

        invoke_async = AsyncMock(side_effect=(tap_process, target_process, dbt_process))

        with mock.patch.object(PluginInvoker, "invoke_async", new=invoke_async):
            result = cli_runner.invoke(cli, args)

            assert "Loader failed" in result.output
            assert result.exit_code == 1

            matcher = EventMatcher(result.stderr)
            assert matcher.event_matches(
                "found ExtractLoadBlocks set",
            )  # tap/target pair
            assert (
                matcher.find_by_event("found PluginCommand")[0]["plugin_type"]
                == "transformers"
            )  # dbt

            completed_events = matcher.find_by_event("Block run completed")
            # there should only be one completed event
            assert len(completed_events) == 1
            assert completed_events[0]["success"] is False
            assert completed_events[0]["duration_seconds"] > 0

            assert completed_events[0]["err"] == "Loader failed"
            assert completed_events[0]["exit_codes"]["loaders"] == 1

            # The tap should NOT have finished, we'll have a write of the
            # SCHEMA message and then nothing further:
            assert matcher.event_matches("SCHEMA")
            assert not matcher.event_matches("RECORD")
            assert not matcher.event_matches("STATE")

            target_stop_event = matcher.find_by_event("target failure")
            assert len(target_stop_event) == 1
            assert target_stop_event[0]["name"] == target.name
            assert target_stop_event[0]["cmd_type"] == "elb"
            assert target_stop_event[0]["stdio"] == "stderr"

            # dbt should not have run at all
            assert not matcher.event_matches("dbt starting")
            assert not matcher.event_matches("dbt running")
            assert not matcher.event_matches("dbt done")

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "dbt",
        "job_logging_service",
    )
    def test_run_elb_target_failure_after_tap_finished(
        self,
        cli_runner,
        tap,
        target,
        tap_process,
        target_process,
        dbt_process,
    ) -> None:
        args = ["run", tap.name, target.name, "dbt:run"]

        target_process.wait.return_value = 1
        target_process.returncode = 1
        target_process.stderr.readline.side_effect = (
            b"target starting\n",
            b"target running\n",
            b"target failure\n",
        )

        invoke_async = AsyncMock(side_effect=(tap_process, target_process, dbt_process))

        with mock.patch.object(PluginInvoker, "invoke_async", new=invoke_async):
            result = cli_runner.invoke(cli, args)

            assert "Loader failed" in result.output
            assert result.exit_code == 1

            matcher = EventMatcher(result.stderr)
            assert matcher.event_matches(
                "found ExtractLoadBlocks set",
            )  # tap/target pair
            assert (
                matcher.find_by_event("found PluginCommand")[0]["plugin_type"]
                == "transformers"
            )  # dbt

            completed_events = matcher.find_by_event("Block run completed")
            # there should only be one completed event
            assert len(completed_events) == 1
            assert completed_events[0]["success"] is False
            assert completed_events[0]["err"] == "Loader failed"
            assert completed_events[0]["exit_codes"]["loaders"] == 1
            assert completed_events[0]["duration_seconds"] > 0

            tap_stop_event = matcher.find_by_event("tap done")
            assert len(tap_stop_event) == 1
            assert tap_stop_event[0]["name"] == tap.name
            assert tap_stop_event[0]["cmd_type"] == "elb"
            assert tap_stop_event[0]["stdio"] == "stderr"

            target_stop_event = matcher.find_by_event("target failure")
            assert len(target_stop_event) == 1
            assert target_stop_event[0]["name"] == target.name
            assert target_stop_event[0]["cmd_type"] == "elb"
            assert target_stop_event[0]["stdio"] == "stderr"

            # dbt should not have run at all
            assert not matcher.event_matches("dbt starting")
            assert not matcher.event_matches("dbt running")
            assert not matcher.event_matches("dbt done")

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "dbt",
        "job_logging_service",
    )
    def test_run_elb_tap_and_target_failed(
        self,
        cli_runner,
        tap,
        target,
        tap_process,
        target_process,
        dbt_process,
    ) -> None:
        args = ["run", tap.name, target.name, "dbt:run"]

        tap_process.wait.return_value = 1
        tap_process.returncode = 1
        tap_process.stderr.readline.side_effect = (
            b"tap starting\n",
            b"tap running\n",
            b"tap failure\n",
        )

        target_process.wait.return_value = 1
        target_process.returncode = 1
        target_process.stderr.readline.side_effect = (
            b"target starting\n",
            b"target running\n",
            b"target failure\n",
        )

        invoke_async = AsyncMock(side_effect=(tap_process, target_process, dbt_process))

        with mock.patch.object(PluginInvoker, "invoke_async", new=invoke_async):
            result = cli_runner.invoke(cli, args)

            assert "Extractor and loader failed" in result.output
            assert result.exit_code == 1

            matcher = EventMatcher(result.stderr)
            assert matcher.event_matches("found ExtractLoadBlocks set")
            assert (
                matcher.find_by_event("found PluginCommand")[0]["plugin_type"]
                == "transformers"
            )

            completed_events = matcher.find_by_event("Block run completed")
            assert len(completed_events) == 1
            assert completed_events[0]["success"] is False
            assert completed_events[0]["duration_seconds"] > 0

            assert completed_events[0]["err"] == "Extractor and loader failed"
            assert completed_events[0]["exit_codes"]["loaders"] == 1

            tap_stop_event = matcher.find_by_event("tap failure")
            assert len(tap_stop_event) == 1
            assert tap_stop_event[0]["name"] == tap.name
            assert tap_stop_event[0]["cmd_type"] == "elb"
            assert tap_stop_event[0]["stdio"] == "stderr"

            target_stop_event = matcher.find_by_event("target failure")
            assert len(target_stop_event) == 1
            assert target_stop_event[0]["name"] == target.name
            assert target_stop_event[0]["cmd_type"] == "elb"
            assert target_stop_event[0]["stdio"] == "stderr"

            # dbt should not have run at all
            assert not matcher.event_matches("dbt starting")
            assert not matcher.event_matches("dbt running")
            assert not matcher.event_matches("dbt done")

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "dbt",
        "dbt_process",
        "job_logging_service",
    )
    def test_run_elb_tap_line_length_limit_error(
        self,
        cli_runner,
        tap,
        target,
        tap_process,
        target_process,
    ) -> None:
        args = ["run", tap.name, target.name]

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
        with mock.patch.object(PluginInvoker, "invoke_async", new=invoke_async):
            result = cli_runner.invoke(cli, args)

            assert "Output line length limit exceeded" in result.output
            assert result.exit_code == 1

            matcher = EventMatcher(result.stderr)

            # tap/target pair
            assert matcher.event_matches("found ExtractLoadBlocks set")

            completed_events = matcher.find_by_event("Block run completed")

            # there should only be one completed event
            assert len(completed_events) == 1
            assert completed_events[0]["success"] is False
            assert completed_events[0]["duration_seconds"] > 0

            assert completed_events[0]["err"] == "Output line length limit exceeded"

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "dbt",
        "dbt_process",
        "job_logging_service",
    )
    def test_run_mapper_config(
        self,
        cli_runner,
        tap,
        target,
        mapper,
        tap_process,
        target_process,
        mapper_process,
        project_add_service,
    ) -> None:
        # exit cleanly when everything is fine
        create_subprocess_exec = AsyncMock(
            side_effect=(tap_process, mapper_process, target_process),
        )

        # no mapper should be found
        args = ["run", tap.name, "not-a-valid-mapping-name", target.name]
        with (
            mock.patch.object(SingerTap, "discover_catalog"),
            mock.patch.object(SingerTap, "apply_catalog_rules"),
            mock.patch("meltano.core.plugin_invoker.asyncio") as asyncio_mock,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec

            result = cli_runner.invoke(cli, args, catch_exceptions=True)
            assert result.exit_code == 1
            assert "Error: Block not-a-valid-mapping-name not found" in result.stderr

        # test mapper/mapping name collision detection - mapper plugin name no mappings
        project_add_service.add(
            PluginType.MAPPERS,
            "mapper-collision-01",
            inherit_from=mapper.name,
        )
        args = ["run", tap.name, "mapper-collision-01", target.name]
        with (
            mock.patch.object(SingerTap, "discover_catalog"),
            mock.patch.object(SingerTap, "apply_catalog_rules"),
            mock.patch("meltano.core.plugin_invoker.asyncio") as asyncio_mock2,
        ):
            asyncio_mock2.create_subprocess_exec = create_subprocess_exec
            with pytest.raises(
                Exception,
                match=(
                    "block violates set requirements: Expected unique mappings "
                    "name not the mapper plugin name: mapper-collision-01"
                ),
            ):
                cli_runner.invoke(cli, args, catch_exceptions=False)

        # Test mapper/mapping name collision detection - mappings name same a
        # mapper plugin name
        project_add_service.add(
            PluginType.MAPPERS,
            "mapper-collision-02",
            inherit_from=mapper.name,
            mappings=[
                {
                    "name": "mapper-collision-02",
                    "config": {
                        "transformations": [
                            {
                                "field_id": "author_email1",
                                "tap_stream_name": "commits1",
                                "type": "MASK-HIDDEN",
                            },
                        ],
                    },
                },
            ],
        )
        args = ["run", tap.name, "mapper-collision-02", target.name]
        with (
            mock.patch.object(SingerTap, "discover_catalog"),
            mock.patch.object(SingerTap, "apply_catalog_rules"),
            mock.patch("meltano.core.plugin_invoker.asyncio") as asyncio_mock2,
        ):
            asyncio_mock2.create_subprocess_exec = create_subprocess_exec
            with pytest.raises(
                Exception,
                match=(
                    "block violates set requirements: Expected unique mappings "
                    "name not the mapper plugin name: mapper-collision-02"
                ),
            ):
                cli_runner.invoke(cli, args, catch_exceptions=False)

        # create duplicate mapping name - should also fail
        project_add_service.add(
            PluginType.MAPPERS,
            "mapper-dupe1",
            inherit_from=mapper.name,
            mappings=[
                {
                    "name": "mock-mapping-dupe",
                    "config": {
                        "transformations": [
                            {
                                "field_id": "author_email1",
                                "tap_stream_name": "commits1",
                                "type": "MASK-HIDDEN",
                            },
                        ],
                    },
                },
            ],
        )
        project_add_service.add(
            PluginType.MAPPERS,
            "mapper-dupe2",
            inherit_from=mapper.name,
            mappings=[
                {
                    "name": "mock-mapping-dupe",
                    "config": {
                        "transformations": [
                            {
                                "field_id": "author_email1",
                                "tap_stream_name": "commits1",
                                "type": "MASK-HIDDEN",
                            },
                        ],
                    },
                },
            ],
        )

        args = ["run", tap.name, "mock-mapping-dupe", target.name]
        with (
            mock.patch.object(SingerTap, "discover_catalog"),
            mock.patch.object(SingerTap, "apply_catalog_rules"),
            mock.patch("meltano.core.plugin_invoker.asyncio") as asyncio_mock2,
        ):
            asyncio_mock2.create_subprocess_exec = create_subprocess_exec
            with pytest.raises(
                AmbiguousMappingName,
                match=(
                    r"Ambiguous mapping name mock-mapping-dupe, found multiple matches."
                ),
            ):
                cli_runner.invoke(cli, args, catch_exceptions=False)

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "dbt",
        "job_logging_service",
    )
    def test_run_elb_mapper_failure(
        self,
        cli_runner,
        tap,
        target,
        mapper,
        tap_process,
        target_process,
        mapper_process,
        dbt_process,
    ) -> None:
        # In this scenario, the map fails on the second read. Target should
        # still complete, but dbt should not.
        args = ["run", tap.name, "mock-mapping-0", target.name, "dbt:run"]

        mapper_process.wait.return_value = 1
        mapper_process.returncode = 1
        mapper_process.stderr.readline.side_effect = (
            b"mapper starting\n",
            b"mapper running\n",
            b"mapper failure\n",
        )

        invoke_async = AsyncMock(
            side_effect=(tap_process, mapper_process, target_process, dbt_process),
        )

        with mock.patch.object(PluginInvoker, "invoke_async", new=invoke_async):
            result = cli_runner.invoke(cli, args, catch_exceptions=True)

            assert "Mappers failed" in result.output
            assert result.exit_code == 1

            matcher = EventMatcher(result.stderr)
            assert matcher.event_matches("found ExtractLoadBlocks set")
            assert (
                matcher.find_by_event("found PluginCommand")[0]["plugin_type"]
                == "transformers"
            )

            completed_events = matcher.find_by_event("Block run completed")
            assert len(completed_events) == 1
            assert completed_events[0]["success"] is False
            assert completed_events[0]["duration_seconds"] > 0

            # the tap should have completed successfully
            matcher.event_matches("tap done")

            # We should see a debug line for from the run manager indicating a
            # intermediate block failed
            matcher.event_matches("Intermediate block in sequence failed.")

            # the failed block should have been the mapper
            mapper_stop_event = matcher.find_by_event("mapper failure")
            assert len(mapper_stop_event) == 1
            assert mapper_stop_event[0]["name"] == mapper.name
            assert mapper_stop_event[0]["cmd_type"] == "elb"
            assert mapper_stop_event[0]["stdio"] == "stderr"

            # target should have attempted to complete
            target_stop_event = matcher.find_by_event("target done")
            assert len(target_stop_event) == 1
            assert target_stop_event[0]["name"] == target.name
            assert target_stop_event[0]["cmd_type"] == "elb"
            assert target_stop_event[0]["stdio"] == "stderr"

            # dbt should not have run at all
            assert not matcher.event_matches("dbt starting")
            assert not matcher.event_matches("dbt running")
            assert not matcher.event_matches("dbt done")

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "mapper",
        "dbt",
        "dbt_process",
        "job_logging_service",
    )
    def test_run_dry_run(
        self,
        cli_runner,
        tap,
        target,
        tap_process,
        target_process,
        mapper_process,
    ) -> None:
        # exit cleanly when everything is fine
        create_subprocess_exec = AsyncMock(
            side_effect=(tap_process, mapper_process, target_process),
        )

        args = ["run", "--dry-run", tap.name, "mock-mapping-0", target.name]
        with (
            mock.patch.object(SingerTap, "discover_catalog"),
            mock.patch.object(SingerTap, "apply_catalog_rules"),
            mock.patch("meltano.core.plugin_invoker.asyncio") as asyncio_mock,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec
            result = cli_runner.invoke(cli, args, catch_exceptions=True)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)

            assert matcher.event_matches(
                "All ExtractLoadBlocks validated, starting execution.",
            )

            # We should have seen the --dry-run specific log line
            assert matcher.event_matches("Dry run, but would have run block 1/1.")

            # We should NOT see any mock done events, and definitely no block
            # completion log lines
            assert not matcher.find_by_event("tap done")
            assert not matcher.find_by_event("target done")
            assert not matcher.find_by_event("Block run completed")
            assert create_subprocess_exec.call_count == 0
            assert asyncio_mock.call_count == 0

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "dbt",
        "job_logging_service",
    )
    def test_run_dry_run_plugin_command(
        self,
        cli_runner,
        dbt_process,
    ) -> None:
        # exit cleanly when everything is fine
        create_subprocess_exec = AsyncMock(side_effect=(dbt_process,))

        args = ["run", "--dry-run", "dbt:run"]
        with (
            mock.patch("meltano.core.plugin_invoker.asyncio") as asyncio_mock,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec
            result = cli_runner.invoke(cli, args, catch_exceptions=True)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)

            events = matcher.find_by_event("Dry run, but would have run block 1/1.")
            assert len(events) == 1
            assert events[0]["comprised_of"] == "dbt:run"

            assert not matcher.find_by_event("dbt done")
            assert create_subprocess_exec.call_count == 0
            assert asyncio_mock.call_count == 0

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures("project")
    @pytest.mark.parametrize("colors", (True, False))
    def test_color_console_exception_handler(
        self,
        colors,
        cli_runner,
        tap,
        target,
        tap_process,
        target_process,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.delenv("FORCE_COLOR", raising=False)
        # toggle color in logging configuration
        logging_config = default_config(log_level="info")
        if not colors:
            logging_config["formatters"]["colored"] = {
                "()": "meltano.core.logging.console_log_formatter",
                "colors": colors,
            }

        # In this scenario, the tap fails on the third read. Target should
        # still complete.
        args = ["run", tap.name, target.name]

        tap_process.wait.return_value = 1
        tap_process.returncode = 1
        tap_process.stderr.readline.side_effect = (
            b"tap starting\n",
            b"tap running\n",
            b"tap failure\n",
        )

        invoke_async = AsyncMock(side_effect=(tap_process, target_process))

        with (
            mock.patch(
                "meltano.core.logging.utils.default_config",
                return_value=logging_config,
            ),
            mock.patch.object(PluginInvoker, "invoke_async", new=invoke_async),
        ):
            result = cli_runner.invoke(cli, args)
            ansi_color_escape = re.compile(r"\x1b\[[0-9;]+m")
            match = ansi_color_escape.search(result.stderr)
            if colors:
                assert match
            else:
                assert not match

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "job_logging_service",
    )
    def test_run_with_timeout_success(
        self,
        cli_runner: MeltanoCliRunner,
        tap,
        target,
        tap_process,
        target_process,
    ) -> None:
        """Test that a run completes successfully when timeout is not exceeded."""
        args = ["run", "--timeout", "30", tap.name, target.name]

        create_subprocess_exec = AsyncMock(side_effect=(tap_process, target_process))

        with (
            mock.patch.object(SingerTap, "discover_catalog"),
            mock.patch.object(SingerTap, "apply_catalog_rules"),
            mock.patch("meltano.core.plugin_invoker.asyncio") as asyncio_mock,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec
            result = cli_runner.invoke(cli, args, catch_exceptions=False)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)
            assert matcher.event_matches("Run timeout configured")
            events = matcher.find_by_event("Run timeout configured")
            assert len(events) == 1
            timeout_config = events[0]
            assert timeout_config["timeout_seconds"] == 30

            events = matcher.find_by_event("Block run completed")
            assert len(events) == 1
            completion_event = events[0]
            assert completion_event["success"]

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "job_logging_service",
    )
    def test_run_with_timeout_exceeded(
        self,
        cli_runner: MeltanoCliRunner,
        tap,
        target,
        tap_process,
        target_process,
    ) -> None:
        """Test that timeout properly terminates a long-running pipeline."""
        args = ["run", "--timeout", "1", tap.name, target.name]

        # Make the tap process take longer than the timeout
        async def long_wait():
            await asyncio.sleep(10)
            return 0

        tap_process.wait.side_effect = long_wait

        create_subprocess_exec = AsyncMock(side_effect=(tap_process, target_process))

        with (
            mock.patch.object(SingerTap, "discover_catalog"),
            mock.patch.object(SingerTap, "apply_catalog_rules"),
            mock.patch("meltano.core.plugin_invoker.asyncio") as asyncio_mock,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec
            result = cli_runner.invoke(cli, args, catch_exceptions=True)
            assert result.exit_code == 1

            matcher = EventMatcher(result.stderr)
            events = matcher.find_by_event("Run timeout configured")
            assert len(events) == 1
            timeout_config = events[0]
            assert timeout_config["timeout_seconds"] == 1
            assert matcher.event_matches("Run timed out")

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "job_logging_service",
        "dbt",
    )
    def test_run_with_timeout_exceeded_plugin_command(
        self,
        cli_runner: MeltanoCliRunner,
        dbt_process,
    ) -> None:
        """Test timeout with plugin commands like dbt:run."""
        args = ["run", "--timeout", "1", "dbt:run"]

        async def long_wait():
            await asyncio.sleep(5)
            return 0

        dbt_process.wait.side_effect = long_wait

        invoke_async = AsyncMock(side_effect=(dbt_process,))

        with mock.patch.object(PluginInvoker, "invoke_async", new=invoke_async):
            result = cli_runner.invoke(cli, args, catch_exceptions=True)
            assert result.exit_code == 1

            matcher = EventMatcher(result.stderr)
            events = matcher.find_by_event("Run timeout configured")
            assert len(events) == 1
            timeout_config = events[0]
            assert timeout_config["timeout_seconds"] == 1
            assert matcher.event_matches("Run timed out")

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "job_logging_service",
    )
    def test_run_with_timeout_environment_variable(
        self,
        cli_runner: MeltanoCliRunner,
        tap,
        target,
        tap_process,
        target_process,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that MELTANO_RUN_TIMEOUT environment variable works."""
        monkeypatch.setenv("MELTANO_RUN_TIMEOUT", "10")
        args = ["run", tap.name, target.name]

        create_subprocess_exec = AsyncMock(side_effect=(tap_process, target_process))

        with (
            mock.patch.object(SingerTap, "discover_catalog"),
            mock.patch.object(SingerTap, "apply_catalog_rules"),
            mock.patch("meltano.core.plugin_invoker.asyncio") as asyncio_mock,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec
            result = cli_runner.invoke(cli, args, catch_exceptions=False)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)
            assert matcher.event_matches("Run timeout configured")

            events = matcher.find_by_event("Run timeout configured")
            assert len(events) == 1
            timeout_config = events[0]
            assert timeout_config["timeout_seconds"] == 10

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "job_logging_service",
    )
    def test_run_with_timeout_zero(
        self,
        cli_runner: MeltanoCliRunner,
        tap,
        target,
    ) -> None:
        """Test that timeout=0 is rejected."""
        args = ["run", "--no-install", "--timeout", "0", tap.name, target.name]

        result = cli_runner.invoke(cli, args, catch_exceptions=True)
        assert result.exit_code == 2
        assert "Invalid value for '--timeout'" in result.output

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "job_logging_service",
        "dbt",
    )
    def test_run_with_timeout_plugin_command(
        self,
        cli_runner: MeltanoCliRunner,
        dbt_process,
    ) -> None:
        """Test timeout with plugin commands like dbt:run."""
        args = ["run", "--timeout", "10", "dbt:run"]

        invoke_async = AsyncMock(side_effect=(dbt_process,))

        with mock.patch.object(PluginInvoker, "invoke_async", new=invoke_async):
            result = cli_runner.invoke(cli, args, catch_exceptions=False)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)
            assert matcher.event_matches("Run timeout configured")
            events = matcher.find_by_event("Run timeout configured")
            assert len(events) == 1
            timeout_config = events[0]
            assert timeout_config["timeout_seconds"] == 10

    @pytest.mark.backend("sqlite")
    @pytest.mark.usefixtures(
        "use_test_log_config",
        "project",
        "job_logging_service",
        "dbt",
    )
    def test_run_with_timeout_multiple_blocks(
        self,
        cli_runner: MeltanoCliRunner,
        tap,
        target,
        tap_process,
        target_process,
        dbt_process,
    ) -> None:
        """Test timeout with multiple blocks in sequence."""
        args = ["run", "--timeout", "10", tap.name, target.name, "dbt:run"]

        invoke_async = AsyncMock(
            side_effect=(tap_process, target_process, dbt_process),
        )

        with mock.patch.object(PluginInvoker, "invoke_async", new=invoke_async):
            result = cli_runner.invoke(cli, args, catch_exceptions=False)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)
            assert matcher.event_matches("Run timeout configured")

            # Should have completed all blocks
            completed_events = matcher.find_by_event("Block run completed")
            assert len(completed_events) == 2
            assert all(event["success"] for event in completed_events)
