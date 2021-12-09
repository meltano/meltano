import asyncio
import json
from typing import List, Optional

import pytest
import structlog
from asynctest import CoroutineMock, mock
from meltano.cli import cli
from meltano.cli.run import generate_job_id, is_command_block
from meltano.core.block.ioblock import IOBlock
from meltano.core.environment import Environment
from meltano.core.logging.formatters import LEVELED_TIMESTAMPED_PRE_CHAIN
from meltano.core.plugin import PluginType
from meltano.core.plugin.singer import SingerTap
from meltano.core.project_plugins_service import PluginAlreadyAddedException
from meltano.core.tracking import GoogleAnalyticsTracker


class MockIOBlock(IOBlock):

    string_id = "mock-io-block"


class TestCliRunUtils:
    def test_is_command_block(self, tap, dbt):
        """Verify that the is_command_block function returns True when the block is an IOBlock and has a command."""
        assert not is_command_block(tap)
        assert is_command_block(dbt)

    def test_generate_job_id(self):
        """Verify that the job id is generated correctly when an environment is provided."""
        block1 = mock.Mock(spec=IOBlock)
        block1.string_id = "block1"

        block2 = mock.Mock(spec=IOBlock)
        block2.string_id = "block2"

        project = mock.Mock()

        project.active_environment = None
        assert not generate_job_id(project, block1, block2)

        project.active_environment = Environment(name="test")
        assert generate_job_id(project, block1, block2) == "test-block1-block2"


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
        side_effect=(b"Starting\n", b"Running\n", b"Done\n")
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
        side_effect=(b"Starting\n", b"Running\n", b"Done\n")
    )
    return target


class EventMatcher:
    def __init__(self, result_output: str):
        """Build a matcher for the result output of a command."""
        self.seen_lines: List[dict] = []

        for line in result_output.splitlines():
            parsed_line = json.loads(line)
            self.seen_lines.append(parsed_line)

    def event_matches(self, event: str) -> bool:
        """Search result output for an event, that matches the given event."""
        for line in self.seen_lines:
            matches = line.get("event") == event
            if matches:
                return True

    def find_by_event(self, event: str) -> Optional[dict]:
        """Return the first matching event, that matches the given event."""
        for line in self.seen_lines:
            matches = line.get("event") == event
            if matches:
                return line


class TestCliRunScratchpadOne:
    @pytest.mark.backend("sqlite")
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    @mock.patch(
        "meltano.core.logging.utils.default_config", return_value=test_log_config
    )
    def test_run_parsing(
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

        with mock.patch.object(SingerTap, "discover_catalog"), mock.patch.object(
            SingerTap, "apply_catalog_rules"
        ), mock.patch(
            "meltano.core.plugin_invoker.asyncio"
        ) as asyncio_mock, mock.patch(
            "meltano.cli.run.ProjectPluginsService",
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
            "meltano.cli.run.ProjectPluginsService",
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
            "meltano.cli.run.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec
            with pytest.raises(
                Exception,
                match="Unknown command type or bad block sequence at index 3, starting block 'target-mock'",
            ):
                result = cli_runner.invoke(cli, args, catch_exceptions=False)
                assert result.exit_code == 1

        args = ["run", tap.name, target.name]
        with mock.patch.object(SingerTap, "discover_catalog"), mock.patch.object(
            SingerTap, "apply_catalog_rules"
        ), mock.patch(
            "meltano.core.plugin_invoker.asyncio"
        ) as asyncio_mock, mock.patch(
            "meltano.cli.run.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec
            result = cli_runner.invoke(cli, args, catch_exceptions=False)
            assert result.exit_code == 0

            matcher = EventMatcher(result.stderr)

            assert matcher.event_matches(
                "All ExtractLoadBlocks validated, starting execution."
            )
            assert matcher.find_by_event("Run call completed.").get("success")
