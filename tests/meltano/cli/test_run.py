import asyncio
import json
from typing import List, Optional

import pytest
import structlog
from asynctest import CoroutineMock, mock
from meltano.cli import cli
from meltano.core.block.ioblock import IOBlock
from meltano.core.logging.formatters import LEVELED_TIMESTAMPED_PRE_CHAIN
from meltano.core.plugin import PluginType
from meltano.core.plugin.singer import SingerTap
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.project_plugins_service import PluginAlreadyAddedException
from meltano.core.tracking import GoogleAnalyticsTracker


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
        process_mock.wait = CoroutineMock(return_value=0)
        process_mock.returncode = 0
        process_mock.stdin.wait_closed = CoroutineMock(return_value=True)
        return process_mock

    return _factory


@pytest.fixture()
def tap_process(process_mock_factory, tap):
    tap = process_mock_factory(tap)
    tap.stdout.at_eof.side_effect = (False, False, False, True)
    tap.stdout.readline = CoroutineMock(
        side_effect=(b"SCHEMA\n", b"RECORD\n", b"STATE\n")
    )
    tap.stderr.at_eof.side_effect = (False, False, False, True)
    tap.stderr.readline = CoroutineMock(
        side_effect=(b"tap starting\n", b"tap running\n", b"tap done\n")
    )
    return tap


@pytest.fixture()
def target_process(process_mock_factory, target):
    target = process_mock_factory(target)

    # Have `target.wait` take 1s to make sure the tap always finishes before the target
    async def wait_mock():
        await asyncio.sleep(1)
        return target.wait.return_value

    target.wait.side_effect = wait_mock

    target.stdout.at_eof.side_effect = (False, False, False, True)
    target.stdout.readline = CoroutineMock(
        side_effect=(b'{"line": 1}\n', b'{"line": 2}\n', b'{"line": 3}\n')
    )
    target.stderr.at_eof.side_effect = (False, False, False, True)
    target.stderr.readline = CoroutineMock(
        side_effect=(b"target starting\n", b"target running\n", b"target done\n")
    )
    return target


@pytest.fixture()
def dbt_process(process_mock_factory, dbt):
    dbt = process_mock_factory(dbt)

    async def wait_mock():
        await asyncio.sleep(1)
        return dbt.wait.return_value

    dbt.wait.side_effect = wait_mock

    dbt.stdout.at_eof.side_effect = (False, True)
    dbt.stdout.readline = CoroutineMock(side_effect=(b"Testoutput"))
    dbt.stderr.at_eof.side_effect = (False, False, False, True)
    dbt.stderr.readline = CoroutineMock(
        side_effect=(b"dbt starting\n", b"dbt running\n", b"dbt done\n")
    )
    return dbt


class EventMatcher:
    def __init__(self, result_output: str):
        """Build a matcher for the result output of a command."""
        self.seen_events: List[dict] = []
        self.seen_raw: List[str] = []

        for line in result_output.splitlines():
            try:
                parsed_line = json.loads(line)
            except json.JSONDecodeError:
                self.seen_raw.append(line)
                continue
            self.seen_events.append(parsed_line)

    def event_matches(self, event: str) -> bool:
        """Search result output for an event, that matches the given event."""
        for line in self.seen_events:
            matches = line.get("event") == event
            if matches:
                return True

    def find_by_event(self, event: str) -> Optional[List[dict]]:
        """Return the first matching event, that matches the given event."""
        matches = []
        for line in self.seen_events:
            match = line.get("event") == event
            if match:
                matches.append(line)
        return matches


class TestCliRunScratchpadOne:
    @pytest.mark.backend("sqlite")
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    @mock.patch(
        "meltano.core.logging.utils.default_config", return_value=test_log_config
    )
    def test_run_parsing_failures(
        self,
        google_tracker,
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
        create_subprocess_exec = CoroutineMock(
            side_effect=(tap_process, target_process)
        )

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
        ) as asyncio_mock, mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec
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
        ) as asyncio_mock, mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec
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
        ) as asyncio_mock, mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec
            result = cli_runner.invoke(cli, args, catch_exceptions=False)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)

            assert matcher.event_matches(
                "All ExtractLoadBlocks validated, starting execution."
            )
            assert matcher.find_by_event("Block run completed.")[0].get("success")

    @pytest.mark.backend("sqlite")
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    @mock.patch(
        "meltano.core.logging.utils.default_config", return_value=test_log_config
    )
    def test_run_basic_invocations(
        self,
        google_tracker,
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
        # exit cleanly when everything is fine
        create_subprocess_exec = CoroutineMock(
            side_effect=(tap_process, target_process)
        )

        # Verify that a vanilla ELB run works
        args = ["run", tap.name, target.name]
        with mock.patch.object(SingerTap, "discover_catalog"), mock.patch.object(
            SingerTap, "apply_catalog_rules"
        ), mock.patch(
            "meltano.core.plugin_invoker.asyncio"
        ) as asyncio_mock, mock.patch(
            "meltano.core.block.parser.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec
            result = cli_runner.invoke(cli, args, catch_exceptions=False)
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
        invoke_async = CoroutineMock(side_effect=(dbt_process,))  # dbt run
        args = ["run", "dbt:run"]
        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ) as invoke_async, mock.patch(
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
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    @mock.patch(
        "meltano.core.logging.utils.default_config", return_value=test_log_config
    )
    def test_run_complex_invocations(
        self,
        google_tracker,
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
        # combine the two scenarios and verify that both a ExtractLoadBlock set and PluginCommand command works
        invoke_async = CoroutineMock(
            side_effect=(tap_process, target_process, dbt_process)
        )  # dbt run
        args = ["run", tap.name, target.name, "dbt:run"]
        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ) as invoke_async, mock.patch(
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
            assert (
                matcher.find_by_event("found PluginCommand")[0].get("plugin_type")
                == "transformers"
            )  # dbt

            # verify that both ExtractLoadBlocks and PluginCommand completed successfully
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
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    @mock.patch(
        "meltano.core.logging.utils.default_config", return_value=test_log_config
    )
    def test_run_plugin_command_failure(
        self,
        google_tracker,
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

        # combine the two scenarios and verify that both a ExtractLoadBlock set and PluginCommand command works
        invoke_async = CoroutineMock(
            side_effect=(tap_process, target_process, dbt_process)
        )

        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ) as invoke_async, mock.patch(
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

            # verify that both ExtractLoadBlocks and PluginCommand completed successfully
            completed_events = matcher.find_by_event("Block run completed.")
            assert len(completed_events) == 1
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

            assert not matcher.event_matches("dbt done")
            assert matcher.event_matches("dbt starting")
            assert matcher.event_matches("dbt running")
            assert matcher.event_matches("dbt failure")

    @pytest.mark.backend("sqlite")
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    @mock.patch(
        "meltano.core.logging.utils.default_config", return_value=test_log_config
    )
    def test_run_elb_failures(
        self,
        google_tracker,
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

        # combine the two scenarios and verify that both a ExtractLoadBlock set and PluginCommand command works
        invoke_async = CoroutineMock(
            side_effect=(tap_process, target_process, dbt_process)
        )

        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ) as invoke_async, mock.patch(
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
            assert matcher.event_matches(
                "found ExtractLoadBlocks set"
            )  # tap/target pair
            assert (
                matcher.find_by_event("found PluginCommand")[0].get("plugin_type")
                == "transformers"
            )  # dbt

            # verify that both ExtractLoadBlocks and PluginCommand completed successfully
            completed_events = matcher.find_by_event("Block run completed.")
            assert (
                len(completed_events) == 1
            )  # there should only be one completed event
            assert completed_events[0].get("success") is False
            assert completed_events[0].get("err") == "RunnerError('Extractor failed')"
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
