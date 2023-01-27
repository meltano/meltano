from __future__ import annotations

import asyncio
import json
import re

import pytest
import structlog
from mock import AsyncMock, mock

from meltano.cli import cli
from meltano.core.block.ioblock import IOBlock
from meltano.core.logging.formatters import LEVELED_TIMESTAMPED_PRE_CHAIN
from meltano.core.logging.job_logging_service import JobLoggingService
from meltano.core.logging.utils import default_config
from meltano.core.plugin import PluginType
from meltano.core.plugin.singer import SingerTap
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.project import Project
from meltano.core.project_plugins_service import PluginAlreadyAddedException


class MockIOBlock(IOBlock):

    string_id = "mock-io-block"


test_log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "test": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
            "foreign_pre_chain": LEVELED_TIMESTAMPED_PRE_CHAIN,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "test",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}


@pytest.fixture(scope="class")
def tap_mock_transform(project_add_service):
    try:
        return project_add_service.add(PluginType.TRANSFORMS, "tap-mock-transform")
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture()
def process_mock_factory():
    def _factory(name):
        process_mock = mock.Mock()
        process_mock.name = name
        process_mock.wait = AsyncMock(return_value=0)
        process_mock.returncode = 0
        process_mock.stdin.wait_closed = AsyncMock(return_value=True)
        return process_mock

    return _factory


@pytest.fixture()
def tap_process(process_mock_factory, tap):
    tap = process_mock_factory(tap)
    tap.stdout.at_eof.side_effect = (False, False, False, True)
    tap.stdout.readline = AsyncMock(side_effect=(b"SCHEMA\n", b"RECORD\n", b"STATE\n"))
    tap.stderr.at_eof.side_effect = (False, False, False, True)
    tap.stderr.readline = AsyncMock(
        side_effect=(b"tap starting\n", b"tap running\n", b"tap done\n")
    )
    return tap


@pytest.fixture()
def target_process(process_mock_factory, target):
    target = process_mock_factory(target)

    # Have `target.wait` take 2s to make sure the tap always finishes before the target
    async def wait_mock():
        await asyncio.sleep(2)
        return target.wait.return_value

    target.wait.side_effect = wait_mock

    target.stdout.at_eof.side_effect = (False, False, False, True)
    target.stdout.readline = AsyncMock(
        side_effect=(b'{"line": 1}\n', b'{"line": 2}\n', b'{"line": 3}\n')
    )
    target.stderr.at_eof.side_effect = (False, False, False, True)
    target.stderr.readline = AsyncMock(
        side_effect=(b"target starting\n", b"target running\n", b"target done\n")
    )
    return target


@pytest.fixture()
def mapper_process(process_mock_factory, mapper):
    mapper = process_mock_factory(mapper)

    # Have `mapper.wait` take 1s to make sure the mapper always finishes after the tap but before the target
    async def wait_mock():
        await asyncio.sleep(1)
        return mapper.wait.return_value

    mapper.wait.side_effect = wait_mock

    mapper.stdout.at_eof.side_effect = (False, False, False, True)
    mapper.stdout.readline = AsyncMock(
        side_effect=(b"SCHEMA\n", b"RECORD\n", b"STATE\n")
    )
    mapper.stderr.at_eof.side_effect = (False, False, False, True)
    mapper.stderr.readline = AsyncMock(
        side_effect=(b"mapper starting\n", b"mapper running\n", b"mapper done\n")
    )
    return mapper


@pytest.fixture()
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
        side_effect=(b"dbt starting\n", b"dbt running\n", b"dbt done\n")
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
            except json.JSONDecodeError:
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
            matches = line.get("event") == event
            if matches:
                return True

    def find_by_event(self, event: str) -> list[dict] | None:
        """Return the first matching event, that matches the given event.

        Args:
            event: the event to search for.

        Returns:
            A list of matching events.
        """
        matches = []
        for line in self.seen_events:
            match = line.get("event") == event
            if match:
                matches.append(line)
        return matches


class TestCliRunScratchpadOne:
    @pytest.mark.backend("sqlite")
    @mock.patch(
        "meltano.core.logging.utils.default_config", return_value=test_log_config
    )
    def test_run_parsing_failures(
        self,
        default_config,
        cli_runner,
        project,
        tap,
        target,
        tap_process,
        target_process,
        project_plugins_service,
        job_logging_service,
    ):
        result = cli_runner.invoke(cli, ["run"])
        assert result.exit_code == 0

        assert EventMatcher(result.stderr).event_matches("No valid blocks found.")

        args = ["run", tap.name]

        # exit cleanly when everything is fine
        create_subprocess_exec = AsyncMock(side_effect=(tap_process, target_process))

        # check that the various ELB validation checks actually run and fail as expected
        with mock.patch.object(SingerTap, "discover_catalog"), mock.patch.object(
            SingerTap, "apply_catalog_rules"
        ), mock.patch(
            "meltano.core.plugin_invoker.asyncio"
        ) as asyncio_mock, mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec
            with pytest.raises(Exception, match="Found no end in block set!"):
                result = cli_runner.invoke(cli, args, catch_exceptions=False)
                assert result.exit_code == 1

        args = ["run", tap.name, tap.name, target.name]
        with mock.patch.object(SingerTap, "discover_catalog"), mock.patch.object(
            SingerTap, "apply_catalog_rules"
        ), mock.patch(
            "meltano.core.plugin_invoker.asyncio"
        ) as asyncio_mock2, mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            asyncio_mock2.create_subprocess_exec = create_subprocess_exec
            with pytest.raises(
                Exception,
                match="Unknown command type or bad block sequence at index 1, starting block 'tap-mock'",
            ):
                result = cli_runner.invoke(cli, args, catch_exceptions=False)
                assert result.exit_code == 1

        args = ["run", tap.name, target.name, target.name]
        with mock.patch.object(SingerTap, "discover_catalog"), mock.patch.object(
            SingerTap, "apply_catalog_rules"
        ), mock.patch(
            "meltano.core.plugin_invoker.asyncio"
        ) as asyncio_mock3, mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            asyncio_mock3.create_subprocess_exec = create_subprocess_exec
            with pytest.raises(
                Exception,
                match="Unknown command type or bad block sequence at index 3, starting block 'target-mock'",
            ):
                result = cli_runner.invoke(cli, args, catch_exceptions=False)
                assert result.exit_code == 1

        # Verify that a vanilla ELB run works
        args = ["run", tap.name, target.name]
        with mock.patch.object(SingerTap, "discover_catalog"), mock.patch.object(
            SingerTap, "apply_catalog_rules"
        ), mock.patch(
            "meltano.core.plugin_invoker.asyncio"
        ) as asyncio_mock4, mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            asyncio_mock4.create_subprocess_exec = create_subprocess_exec
            result = cli_runner.invoke(cli, args, catch_exceptions=False)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)

            assert matcher.event_matches(
                "All ExtractLoadBlocks validated, starting execution."
            )
            assert matcher.find_by_event("Block run completed.")[0].get("success")

    @pytest.mark.backend("sqlite")
    @mock.patch(
        "meltano.core.logging.utils.default_config", return_value=test_log_config
    )
    def test_run_basic_invocations(
        self,
        default_config,
        cli_runner,
        project,
        tap,
        target,
        mapper,
        dbt,
        tap_process,
        target_process,
        mapper_process,
        dbt_process,
        project_plugins_service,
        job_logging_service,
    ):
        # exit cleanly when everything is fine
        create_subprocess_exec = AsyncMock(
            side_effect=(tap_process, mapper_process, target_process)
        )

        # Verify that a vanilla ELB run works
        args = ["run", tap.name, "mock-mapping-0", target.name]
        with mock.patch.object(SingerTap, "discover_catalog"), mock.patch.object(
            SingerTap, "apply_catalog_rules"
        ), mock.patch(
            "meltano.core.plugin_invoker.asyncio"
        ) as asyncio_mock, mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec
            result = cli_runner.invoke(cli, args, catch_exceptions=True)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)

            assert matcher.event_matches(
                "All ExtractLoadBlocks validated, starting execution."
            )
            target_stop_event = matcher.find_by_event("target done")
            assert len(target_stop_event) == 1
            assert target_stop_event[0].get("name") == target.name
            assert target_stop_event[0].get("cmd_type") == "elb"
            assert target_stop_event[0].get("stdio") == "stderr"
            assert matcher.find_by_event("Block run completed.")[0].get("success")

        # Verify that a vanilla command plugin (dbt:run) run works
        invoke_async = AsyncMock(side_effect=(dbt_process,))  # dbt run
        args = ["run", "dbt:run"]
        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ), mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch(
            "meltano.core.transform_add_service.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, args, catch_exceptions=False)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)
            assert (
                matcher.find_by_event("found plugin in cli invocation")[0].get(
                    "plugin_name"
                )
                == "dbt"
            )
            dbt_start_event = matcher.find_by_event("dbt done")
            assert len(dbt_start_event) == 1
            assert dbt_start_event[0].get("name") == "dbt"
            assert dbt_start_event[0].get("cmd_type") == "command"
            assert dbt_start_event[0].get("stdio") == "stderr"
            assert matcher.find_by_event("Block run completed.")[0].get("success")

    @pytest.mark.backend("sqlite")
    @mock.patch(
        "meltano.core.logging.utils.default_config", return_value=test_log_config
    )
    def test_run_custom_suffix_command_option(
        self,
        default_config,
        cli_runner,
        project,
        tap,
        target,
        tap_process,
        target_process,
        project_plugins_service,
        job_logging_service: JobLoggingService,
    ):
        # exit cleanly when everything is fine
        create_subprocess_exec = AsyncMock(side_effect=(tap_process, target_process))

        # verify that a state ID with custom suffix from command option is generated for an ELB run
        args = ["run", tap.name, target.name, "--state-id-suffix", "test-suffix"]

        with mock.patch.object(SingerTap, "discover_catalog"), mock.patch.object(
            SingerTap, "apply_catalog_rules"
        ), mock.patch(
            "meltano.core.plugin_invoker.asyncio"
        ) as asyncio_mock, mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec
            result = cli_runner.invoke(cli, args, catch_exceptions=True)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)
            assert matcher.find_by_event("Block run completed.")[0].get("success")

            job_logging_service.get_latest_log(
                f"dev:{tap.name}-to-{target.name}:test-suffix"
            )

    @pytest.mark.backend("sqlite")
    @pytest.mark.parametrize(
        "suffix_args",
        [
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
        ],
        ids=[
            "static",
            "dynamic (single env)",
            "dynamic (multiple env)",
        ],
    )
    @mock.patch(
        "meltano.core.logging.utils.default_config", return_value=test_log_config
    )
    def test_run_custom_suffix_active_environment(
        self,
        default_config,
        suffix_args,
        cli_runner,
        project: Project,
        tap,
        target,
        tap_process,
        target_process,
        project_plugins_service,
        job_logging_service: JobLoggingService,
    ):
        state_id_suffix, expected_suffix, suffix_env = suffix_args

        # exit cleanly when everything is fine
        create_subprocess_exec = AsyncMock(side_effect=(tap_process, target_process))

        # verify that a state ID with custom suffix from active environment is generated for an ELB run
        project.activate_environment("dev")
        project.active_environment.state_id_suffix = state_id_suffix

        args = ["run", tap.name, target.name]

        with mock.patch.object(SingerTap, "discover_catalog"), mock.patch.object(
            SingerTap, "apply_catalog_rules"
        ), mock.patch(
            "meltano.core.plugin_invoker.asyncio"
        ) as asyncio_mock, mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ), pytest.MonkeyPatch().context() as mp:
            asyncio_mock.create_subprocess_exec = create_subprocess_exec

            for env in suffix_env:
                mp.setenv(*env)

            result = cli_runner.invoke(cli, args, catch_exceptions=True)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)
            assert matcher.find_by_event("Block run completed.")[0].get("success")

            job_logging_service.get_latest_log(
                f"dev:{tap.name}-to-{target.name}:${expected_suffix}"
            )

    @pytest.mark.backend("sqlite")
    @mock.patch(
        "meltano.core.logging.utils.default_config", return_value=test_log_config
    )
    def test_run_multiple_commands(
        self,
        default_config,
        cli_runner,
        project,
        dbt,
        dbt_process,
        project_plugins_service,
        job_logging_service,
    ):
        # Verify that requesting the same command plugin multiple time with different args works
        invoke_async = AsyncMock(
            side_effect=(
                dbt_process,
                dbt_process,
            )
        )
        args = ["run", "dbt:test", "dbt:run"]
        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ), mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch(
            "meltano.core.transform_add_service.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, args, catch_exceptions=False)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)
            assert (
                matcher.find_by_event("found plugin in cli invocation")[0].get(
                    "plugin_name"
                )
                == "dbt"
            )

            command_add_events = matcher.find_by_event(
                "plugin command added for execution"
            )

            assert len(command_add_events) == 2
            assert invoke_async.call_count == 2

            assert command_add_events[0].get("command_name") == "test"
            assert invoke_async.mock_calls[0][2]["command"] == "test"

            assert command_add_events[1].get("command_name") == "run"
            assert invoke_async.mock_calls[1][2]["command"] == "run"

            assert matcher.find_by_event("Block run completed.")[0].get("success")
            assert matcher.find_by_event("Block run completed.")[1].get("success")

    @pytest.mark.backend("sqlite")
    @mock.patch(
        "meltano.core.logging.utils.default_config", return_value=test_log_config
    )
    def test_run_complex_invocations(
        self,
        default_config,
        cli_runner,
        project,
        tap,
        target,
        mapper,
        dbt,
        tap_process,
        target_process,
        mapper_process,
        dbt_process,
        project_plugins_service,
        job_logging_service,
    ):
        invoke_async = AsyncMock(
            side_effect=(tap_process, mapper_process, target_process, dbt_process)
        )
        args = ["run", tap.name, "mock-mapping-0", target.name, "dbt:run"]
        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ), mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch(
            "meltano.core.transform_add_service.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, args, catch_exceptions=False)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)
            assert matcher.event_matches(
                "found ExtractLoadBlocks set"
            )  # tap/target pair

            # make sure mapper was found and at its expected positions
            for ev in matcher.find_by_event("found block"):
                if ev.get("block_type") == "mappers":
                    assert ev.get("index") == 1

            assert (
                matcher.find_by_event("found PluginCommand")[0].get("plugin_type")
                == "transformers"
            )  # dbt

            completed_events = matcher.find_by_event("Block run completed.")
            assert len(completed_events) == 2
            for event in completed_events:
                assert event.get("success")

            tap_stop_event = matcher.find_by_event("tap done")
            assert len(tap_stop_event) == 1
            assert tap_stop_event[0].get("name") == tap.name
            assert tap_stop_event[0].get("cmd_type") == "elb"
            assert tap_stop_event[0].get("stdio") == "stderr"

            target_stop_event = matcher.find_by_event("target done")
            assert len(target_stop_event) == 1
            assert target_stop_event[0].get("name") == target.name
            assert target_stop_event[0].get("cmd_type") == "elb"
            assert target_stop_event[0].get("stdio") == "stderr"

            dbt_done_event = matcher.find_by_event("dbt done")
            assert len(dbt_done_event) == 1
            assert dbt_done_event[0].get("name") == "dbt"
            assert dbt_done_event[0].get("cmd_type") == "command"
            assert dbt_done_event[0].get("stdio") == "stderr"

    @pytest.mark.backend("sqlite")
    @mock.patch(
        "meltano.core.logging.utils.default_config", return_value=test_log_config
    )
    def test_run_plugin_command_failure(
        self,
        default_config,
        cli_runner,
        project,
        tap,
        target,
        dbt,
        tap_process,
        target_process,
        dbt_process,
        project_plugins_service,
        job_logging_service,
    ):
        args = ["run", tap.name, target.name, "dbt:run"]

        dbt_process.wait.return_value = 1
        dbt_process.returncode = 1
        dbt_process.stderr.readline.side_effect = (
            b"dbt starting\n",
            b"dbt running\n",
            b"dbt failure\n",
        )

        invoke_async = AsyncMock(side_effect=(tap_process, target_process, dbt_process))

        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ), mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch(
            "meltano.core.transform_add_service.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert "`dbt run` failed" in str(result.exception)

            matcher = EventMatcher(result.stderr)
            assert matcher.event_matches(
                "found ExtractLoadBlocks set"
            )  # tap/target pair
            assert (
                matcher.find_by_event("found PluginCommand")[0].get("plugin_type")
                == "transformers"
            )  # dbt

            completed_events = matcher.find_by_event("Block run completed.")
            assert len(completed_events) == 2
            for event in completed_events:
                if event.get("block_type") == "ExtractLoadBlocks":
                    assert event.get("success")
                elif event.get("block_type") == "InvokerCommand":
                    assert event.get("success") is False

            tap_stop_event = matcher.find_by_event("tap done")
            assert len(tap_stop_event) == 1
            assert tap_stop_event[0].get("name") == tap.name
            assert tap_stop_event[0].get("cmd_type") == "elb"
            assert tap_stop_event[0].get("stdio") == "stderr"

            target_stop_event = matcher.find_by_event("target done")
            assert len(target_stop_event) == 1
            assert target_stop_event[0].get("name") == target.name
            assert target_stop_event[0].get("cmd_type") == "elb"
            assert target_stop_event[0].get("stdio") == "stderr"

            assert not matcher.event_matches("dbt done")
            assert matcher.event_matches("dbt starting")
            assert matcher.event_matches("dbt running")
            assert matcher.event_matches("dbt failure")

    @pytest.mark.backend("sqlite")
    @mock.patch(
        "meltano.core.logging.utils.default_config", return_value=test_log_config
    )
    def test_run_elb_tap_failure(
        self,
        default_config,
        cli_runner,
        project,
        tap,
        target,
        dbt,
        tap_process,
        target_process,
        dbt_process,
        project_plugins_service,
        job_logging_service,
    ):

        # in this scenario, the tap fails on the third read. Target should still complete, but dbt should not.
        args = ["run", tap.name, target.name, "dbt:run"]

        tap_process.wait.return_value = 1
        tap_process.returncode = 1
        tap_process.stderr.readline.side_effect = (
            b"tap starting\n",
            b"tap running\n",
            b"tap failure\n",
        )

        invoke_async = AsyncMock(side_effect=(tap_process, target_process, dbt_process))

        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ), mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch(
            "meltano.core.transform_add_service.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, args)

            assert (
                "Run invocation could not be completed as block failed: Extractor failed"
                in str(result.exception)
            )
            assert result.exit_code == 1

            matcher = EventMatcher(result.stderr)
            assert matcher.event_matches("found ExtractLoadBlocks set")
            assert (
                matcher.find_by_event("found PluginCommand")[0].get("plugin_type")
                == "transformers"
            )

            completed_events = matcher.find_by_event("Block run completed.")
            assert len(completed_events) == 1
            assert completed_events[0].get("success") is False

            # or is hack to work around python 3.6 failures
            assert (
                completed_events[0].get("err") == "RunnerError('Extractor failed',)"
                or "RunnerError('Extractor failed')"
            )
            assert completed_events[0].get("exit_codes").get("extractors") == 1

            tap_stop_event = matcher.find_by_event("tap failure")
            assert len(tap_stop_event) == 1
            assert tap_stop_event[0].get("name") == tap.name
            assert tap_stop_event[0].get("cmd_type") == "elb"
            assert tap_stop_event[0].get("stdio") == "stderr"

            target_stop_event = matcher.find_by_event("target done")
            assert len(target_stop_event) == 1
            assert target_stop_event[0].get("name") == target.name
            assert target_stop_event[0].get("cmd_type") == "elb"
            assert target_stop_event[0].get("stdio") == "stderr"

            # dbt should not have run at all
            assert not matcher.event_matches("dbt starting")
            assert not matcher.event_matches("dbt running")
            assert not matcher.event_matches("dbt done")

    @pytest.mark.backend("sqlite")
    @mock.patch(
        "meltano.core.logging.utils.default_config", return_value=test_log_config
    )
    def test_run_elb_target_failure_before_tap_finished(  # noqa: WPS118
        self,
        default_config,
        cli_runner,
        project,
        tap,
        target,
        dbt,
        tap_process,
        target_process,
        dbt_process,
        project_plugins_service,
        job_logging_service,
    ):

        args = ["run", tap.name, target.name, "dbt:run"]

        # Have `tap_process.wait` take 2s to make sure the target can fail before tap finishes
        async def tap_wait_mock():
            await asyncio.sleep(2)
            return tap_process.wait.return_value

        tap_process.wait.side_effect = tap_wait_mock

        # Writing to target stdin will fail because (we'll pretend) it has already died
        target_process.stdin = mock.Mock(spec=asyncio.StreamWriter)
        # capture_subprocess_output writer will return and close the pipe when either BrokenPipeError or ConnectionResetError is enccountered
        # it does not itself reraise the exception - so you shouldn't expect to see these.
        target_process.stdin.write.side_effect = BrokenPipeError
        target_process.stdin.drain = AsyncMock(side_effect=ConnectionResetError)
        target_process.stdin.wait_closed = AsyncMock(return_value=True)

        # Have `target_process.wait` take 1s to make sure the `stdin.write`/`drain` exceptions can be raised
        async def target_wait_mock():
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

        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ), mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch(
            "meltano.core.transform_add_service.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, args)

            assert (
                "Run invocation could not be completed as block failed: Loader failed"
                in str(result.exception)
            )
            assert result.exit_code == 1

            matcher = EventMatcher(result.stderr)
            assert matcher.event_matches(
                "found ExtractLoadBlocks set"
            )  # tap/target pair
            assert (
                matcher.find_by_event("found PluginCommand")[0].get("plugin_type")
                == "transformers"
            )  # dbt

            completed_events = matcher.find_by_event("Block run completed.")
            # there should only be one completed event
            assert len(completed_events) == 1
            assert completed_events[0].get("success") is False

            # or is hack to work around python 3.6 failures
            assert (
                completed_events[0].get("err") == "RunnerError('Loader failed',)"
                or "RunnerError('Loader failed')"
            )
            assert completed_events[0].get("exit_codes").get("loaders") == 1

            # the tap should NOT have finished, we'll have a write of the SCHEMA message and then nothing further:
            assert matcher.event_matches("SCHEMA")
            assert not matcher.event_matches("RECORD")
            assert not matcher.event_matches("STATE")

            target_stop_event = matcher.find_by_event("target failure")
            assert len(target_stop_event) == 1
            assert target_stop_event[0].get("name") == target.name
            assert target_stop_event[0].get("cmd_type") == "elb"
            assert target_stop_event[0].get("stdio") == "stderr"

            # dbt should not have run at all
            assert not matcher.event_matches("dbt starting")
            assert not matcher.event_matches("dbt running")
            assert not matcher.event_matches("dbt done")

    @pytest.mark.backend("sqlite")
    @mock.patch(
        "meltano.core.logging.utils.default_config", return_value=test_log_config
    )
    def test_run_elb_target_failure_after_tap_finished(  # noqa: WPS118
        self,
        default_config,
        cli_runner,
        project,
        tap,
        target,
        dbt,
        tap_process,
        target_process,
        dbt_process,
        project_plugins_service,
        job_logging_service,
    ):

        args = ["run", tap.name, target.name, "dbt:run"]

        target_process.wait.return_value = 1
        target_process.returncode = 1
        target_process.stderr.readline.side_effect = (
            b"target starting\n",
            b"target running\n",
            b"target failure\n",
        )

        invoke_async = AsyncMock(side_effect=(tap_process, target_process, dbt_process))

        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ), mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch(
            "meltano.core.transform_add_service.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, args)

            assert (
                "Run invocation could not be completed as block failed: Loader failed"
                in str(result.exception)
            )
            assert result.exit_code == 1

            matcher = EventMatcher(result.stderr)
            assert matcher.event_matches(
                "found ExtractLoadBlocks set"
            )  # tap/target pair
            assert (
                matcher.find_by_event("found PluginCommand")[0].get("plugin_type")
                == "transformers"
            )  # dbt

            completed_events = matcher.find_by_event("Block run completed.")
            # there should only be one completed event
            assert len(completed_events) == 1
            assert completed_events[0].get("success") is False
            # or is hack to work around python 3.6 failures
            assert (
                completed_events[0].get("err") == "RunnerError('Loader failed',)"
                or "RunnerError('Loader failed')"
            )
            assert completed_events[0].get("exit_codes").get("loaders") == 1

            tap_stop_event = matcher.find_by_event("tap done")
            assert len(tap_stop_event) == 1
            assert tap_stop_event[0].get("name") == tap.name
            assert tap_stop_event[0].get("cmd_type") == "elb"
            assert tap_stop_event[0].get("stdio") == "stderr"

            target_stop_event = matcher.find_by_event("target failure")
            assert len(target_stop_event) == 1
            assert target_stop_event[0].get("name") == target.name
            assert target_stop_event[0].get("cmd_type") == "elb"
            assert target_stop_event[0].get("stdio") == "stderr"

            # dbt should not have run at all
            assert not matcher.event_matches("dbt starting")
            assert not matcher.event_matches("dbt running")
            assert not matcher.event_matches("dbt done")

    @pytest.mark.backend("sqlite")
    @mock.patch(
        "meltano.core.logging.utils.default_config", return_value=test_log_config
    )
    def test_run_elb_tap_and_target_failed(
        self,
        default_config,
        cli_runner,
        project,
        tap,
        target,
        dbt,
        tap_process,
        target_process,
        dbt_process,
        project_plugins_service,
        job_logging_service,
    ):

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

        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ), mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch(
            "meltano.core.transform_add_service.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, args)

            assert (
                "Run invocation could not be completed as block failed: Extractor and loader failed"
                in str(result.exception)
            )
            assert result.exit_code == 1

            matcher = EventMatcher(result.stderr)
            assert matcher.event_matches("found ExtractLoadBlocks set")
            assert (
                matcher.find_by_event("found PluginCommand")[0].get("plugin_type")
                == "transformers"
            )

            completed_events = matcher.find_by_event("Block run completed.")
            assert len(completed_events) == 1
            assert completed_events[0].get("success") is False

            # or is hack to work around python 3.6 failures
            assert (
                completed_events[0].get("err")
                == "RunnerError('Extractor and loader failed',)"
                or "RunnerError('Extractor and loader failed')"
            )
            assert completed_events[0].get("exit_codes").get("loaders") == 1

            tap_stop_event = matcher.find_by_event("tap failure")
            assert len(tap_stop_event) == 1
            assert tap_stop_event[0].get("name") == tap.name
            assert tap_stop_event[0].get("cmd_type") == "elb"
            assert tap_stop_event[0].get("stdio") == "stderr"

            target_stop_event = matcher.find_by_event("target failure")
            assert len(target_stop_event) == 1
            assert target_stop_event[0].get("name") == target.name
            assert target_stop_event[0].get("cmd_type") == "elb"
            assert target_stop_event[0].get("stdio") == "stderr"

            # dbt should not have run at all
            assert not matcher.event_matches("dbt starting")
            assert not matcher.event_matches("dbt running")
            assert not matcher.event_matches("dbt done")

    @pytest.mark.backend("sqlite")
    @mock.patch(
        "meltano.core.logging.utils.default_config", return_value=test_log_config
    )
    def test_run_elb_tap_line_length_limit_error(
        self,
        default_config,
        cli_runner,
        project,
        tap,
        target,
        dbt,
        tap_process,
        target_process,
        dbt_process,
        project_plugins_service,
        job_logging_service,
    ):

        args = ["run", tap.name, target.name]

        # Raise a ValueError wrapping a LimitOverrunError, like StreamReader.readline does:
        # https://github.com/python/cpython/blob/v3.8.7/Lib/asyncio/streams.py#L549
        try:  # noqa: WPS328
            raise asyncio.LimitOverrunError(
                "Separator is not found, and chunk exceed the limit", 0
            )
        except asyncio.LimitOverrunError as err:
            try:  # noqa: WPS328, WPS505
                # `ValueError` needs to be raised from inside the except block
                # for `LimitOverrunError` so that `__context__` is set.
                raise ValueError(str(err))
            except ValueError as wrapper_err:
                tap_process.stdout.readline.side_effect = wrapper_err

        # Have `tap_process.wait` take 1s to make sure the LimitOverrunError exception can be raised before tap finishes
        async def wait_mock():
            await asyncio.sleep(1)
            return tap_process.wait.return_value

        tap_process.wait.side_effect = wait_mock

        invoke_async = AsyncMock(side_effect=(tap_process, target_process))
        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ), mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch(
            "meltano.core.transform_add_service.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, args)

            assert (
                "Run invocation could not be completed as block failed: Output line length limit exceeded"
                in str(result.exception)
            )
            assert result.exit_code == 1

            matcher = EventMatcher(result.stderr)

            # tap/target pair
            assert matcher.event_matches("found ExtractLoadBlocks set")

            completed_events = matcher.find_by_event("Block run completed.")

            # there should only be one completed event
            assert len(completed_events) == 1
            assert completed_events[0].get("success") is False

            # or is hack to work around python 3.6 failures
            assert (
                completed_events[0].get("err")
                == "RunnerError('Output line length limit exceeded',)"
                or "RunnerError('Output line length limit exceeded')"
            )

    @pytest.mark.backend("sqlite")
    @mock.patch(
        "meltano.core.logging.utils.default_config", return_value=test_log_config
    )
    def test_run_mapper_config(
        self,
        default_config,
        cli_runner,
        project,
        tap,
        target,
        mapper,
        dbt,
        tap_process,
        target_process,
        mapper_process,
        dbt_process,
        project_plugins_service,
        job_logging_service,
        project_add_service,
    ):
        # exit cleanly when everything is fine
        create_subprocess_exec = AsyncMock(
            side_effect=(tap_process, mapper_process, target_process)
        )

        # no mapper should be found
        args = ["run", tap.name, "not-a-valid-mapping-name", target.name]
        with mock.patch.object(SingerTap, "discover_catalog"), mock.patch.object(
            SingerTap, "apply_catalog_rules"
        ), mock.patch(
            "meltano.core.plugin_invoker.asyncio"
        ) as asyncio_mock, mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec

            result = cli_runner.invoke(cli, args, catch_exceptions=True)
            assert result.exit_code == 1
            assert "Error: Block not-a-valid-mapping-name not found" in result.stderr

        # test mapper/mapping name collision detection - mapper plugin name no mappings
        project_add_service.add(
            PluginType.MAPPERS, "mapper-collision-01", inherit_from=mapper.name
        )
        args = ["run", tap.name, "mapper-collision-01", target.name]
        with mock.patch.object(SingerTap, "discover_catalog"), mock.patch.object(
            SingerTap, "apply_catalog_rules"
        ), mock.patch(
            "meltano.core.plugin_invoker.asyncio"
        ) as asyncio_mock2, mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            asyncio_mock2.create_subprocess_exec = create_subprocess_exec
            with pytest.raises(
                Exception,
                match="block violates set requirements: Expected unique mappings name not the mapper plugin name: mapper-collision-01",
            ):
                result = cli_runner.invoke(cli, args, catch_exceptions=False)
                assert result.exit_code == 1

        # test mapper/mapping name collision detection - mappings name same a mapper plugin name
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
                            }
                        ]
                    },
                }
            ],
        )
        args = ["run", tap.name, "mapper-collision-02", target.name]
        with mock.patch.object(SingerTap, "discover_catalog"), mock.patch.object(
            SingerTap, "apply_catalog_rules"
        ), mock.patch(
            "meltano.core.plugin_invoker.asyncio"
        ) as asyncio_mock2, mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            asyncio_mock2.create_subprocess_exec = create_subprocess_exec
            with pytest.raises(
                Exception,
                match="block violates set requirements: Expected unique mappings name not the mapper plugin name: mapper-collision-02",
            ):
                result = cli_runner.invoke(cli, args, catch_exceptions=False)
                assert result.exit_code == 1

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
                            }
                        ]
                    },
                }
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
                            }
                        ]
                    },
                }
            ],
        )

        args = ["run", tap.name, "mock-mapping-dupe", target.name]
        with mock.patch.object(SingerTap, "discover_catalog"), mock.patch.object(
            SingerTap, "apply_catalog_rules"
        ), mock.patch(
            "meltano.core.plugin_invoker.asyncio"
        ) as asyncio_mock2, mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            asyncio_mock2.create_subprocess_exec = create_subprocess_exec

            result = cli_runner.invoke(cli, args, catch_exceptions=True)
            assert result.exit_code == 1
            assert (
                "Error: Ambiguous mapping name mock-mapping-dupe, found multiple matches."
                in result.stderr
            )

    @pytest.mark.backend("sqlite")
    @mock.patch(
        "meltano.core.logging.utils.default_config", return_value=test_log_config
    )
    def test_run_elb_mapper_failure(
        self,
        default_config,
        cli_runner,
        project,
        tap,
        target,
        mapper,
        dbt,
        tap_process,
        target_process,
        mapper_process,
        dbt_process,
        project_plugins_service,
        job_logging_service,
    ):

        # in this scenario, the map fails on the second read. Target should still complete, but dbt should not.
        args = ["run", tap.name, "mock-mapping-0", target.name, "dbt:run"]

        mapper_process.wait.return_value = 1
        mapper_process.returncode = 1
        mapper_process.stderr.readline.side_effect = (
            b"mapper starting\n",
            b"mapper running\n",
            b"mapper failure\n",
        )

        invoke_async = AsyncMock(
            side_effect=(tap_process, mapper_process, target_process, dbt_process)
        )

        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ), mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch(
            "meltano.core.transform_add_service.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, args, catch_exceptions=True)

            assert "Mappers failed" in str(result.exception)
            assert result.exit_code == 1

            matcher = EventMatcher(result.stderr)
            assert matcher.event_matches("found ExtractLoadBlocks set")
            assert (
                matcher.find_by_event("found PluginCommand")[0].get("plugin_type")
                == "transformers"
            )

            completed_events = matcher.find_by_event("Block run completed.")
            assert len(completed_events) == 1
            assert completed_events[0].get("success") is False

            # the tap should have completed successfully
            matcher.event_matches("tap done")

            # we should see a debug line for from the run manager indicating a intermediate block failed
            matcher.event_matches("Intermediate block in sequence failed.")

            # the failed block should have been the mapper
            mapper_stop_event = matcher.find_by_event("mapper failure")
            assert len(mapper_stop_event) == 1
            assert mapper_stop_event[0].get("name") == mapper.name
            assert mapper_stop_event[0].get("cmd_type") == "elb"
            assert mapper_stop_event[0].get("stdio") == "stderr"

            # target should have attempted to complete
            target_stop_event = matcher.find_by_event("target done")
            assert len(target_stop_event) == 1
            assert target_stop_event[0].get("name") == target.name
            assert target_stop_event[0].get("cmd_type") == "elb"
            assert target_stop_event[0].get("stdio") == "stderr"

            # dbt should not have run at all
            assert not matcher.event_matches("dbt starting")
            assert not matcher.event_matches("dbt running")
            assert not matcher.event_matches("dbt done")

    @pytest.mark.backend("sqlite")
    @mock.patch(
        "meltano.core.logging.utils.default_config", return_value=test_log_config
    )
    def test_run_dry_run(
        self,
        default_config,
        cli_runner,
        project,
        tap,
        target,
        mapper,
        dbt,
        tap_process,
        target_process,
        mapper_process,
        dbt_process,
        project_plugins_service,
        job_logging_service,
    ):
        # exit cleanly when everything is fine
        create_subprocess_exec = AsyncMock(
            side_effect=(tap_process, mapper_process, target_process)
        )

        args = ["run", "--dry-run", tap.name, "mock-mapping-0", target.name]
        with mock.patch.object(SingerTap, "discover_catalog"), mock.patch.object(
            SingerTap, "apply_catalog_rules"
        ), mock.patch(
            "meltano.core.plugin_invoker.asyncio"
        ) as asyncio_mock, mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec
            result = cli_runner.invoke(cli, args, catch_exceptions=True)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)

            assert matcher.event_matches(
                "All ExtractLoadBlocks validated, starting execution."
            )

            # we should have seen the --dry-run specific log line
            assert matcher.event_matches("Dry run, but would have run block 1/1.")

            # we should NOT see any mock done events, and definitely no block completion log lines
            assert not matcher.find_by_event("tap done")
            assert not matcher.find_by_event("target done")
            assert not matcher.find_by_event("Block run completed.")
            assert create_subprocess_exec.call_count == 0
            assert asyncio_mock.call_count == 0

    @pytest.mark.backend("sqlite")
    @pytest.mark.parametrize(
        "colors",
        [True, False],
    )
    def test_color_console_exception_handler(
        self,
        colors,
        cli_runner,
        project,
        tap,
        target,
        tap_process,
        target_process,
        project_plugins_service,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.delenv("FORCE_COLOR", raising=False)
        # toggle color in logging configuration
        logging_config = default_config(log_level="info")
        if not colors:
            logging_config["formatters"]["colored"] = {
                "()": "meltano.core.logging.console_log_formatter",
                "colors": colors,
            }

        # in this scenario, the tap fails on the third read. Target should still complete.
        args = ["run", tap.name, target.name]

        tap_process.wait.return_value = 1
        tap_process.returncode = 1
        tap_process.stderr.readline.side_effect = (
            b"tap starting\n",
            b"tap running\n",
            b"tap failure\n",
        )

        invoke_async = AsyncMock(side_effect=(tap_process, target_process))

        with mock.patch(
            "meltano.core.logging.utils.default_config", return_value=logging_config
        ), mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ), mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch(
            "meltano.core.transform_add_service.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, args)
            ansi_color_escape = re.compile(r"\x1b\[[0-9;]+m")
            match = ansi_color_escape.search(result.stderr)
            if colors:
                assert match
            else:
                assert not match
