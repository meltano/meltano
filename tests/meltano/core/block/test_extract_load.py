from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path

import mock
import pytest
from mock import AsyncMock

from meltano.core.block.blockset import BlockSetValidationError
from meltano.core.block.extract_load import (
    ELBContext,
    ELBContextBuilder,
    ExtractLoadBlocks,
    generate_state_id,
)
from meltano.core.block.ioblock import IOBlock
from meltano.core.block.singer import SingerBlock
from meltano.core.environment import Environment
from meltano.core.job import Job, Payload, State
from meltano.core.job_state import STATE_ID_COMPONENT_DELIMITER
from meltano.core.logging import OutputLogger
from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.project_plugins_service import PluginAlreadyAddedException
from meltano.core.runner import RunnerError
from meltano.core.runner.singer import SingerRunner

TEST_STATE_ID = "test_job"
MOCK_STATE_MESSAGE = json.dumps({"type": "STATE"})
MOCK_RECORD_MESSAGE = json.dumps({"type": "RECORD"})


def create_plugin_files(config_dir: Path, plugin: ProjectPlugin):
    for file in plugin.config_files.values():
        Path(os.path.join(config_dir, file)).touch()

    return config_dir


@pytest.fixture
def test_job(session) -> Job:
    return Job(
        job_name=TEST_STATE_ID,
        state=State.SUCCESS,
        payload_flags=Payload.STATE,
        payload={"singer_state": {"bookmarks": []}},
    ).save(session)


@pytest.fixture
def output_logger() -> OutputLogger:
    return OutputLogger("test.log")


@pytest.fixture
def elb_context(project, session, test_job, output_logger) -> ELBContext:
    ctx = ELBContext(
        project=project,
        job=test_job,
        base_output_logger=output_logger,
    )
    ctx.session = session
    return ctx


class TestELBContext:
    def test_elt_run_dir_is_returned(self, project, test_job, elb_context: ELBContext):
        expected_path = project.job_dir(test_job.job_name, str(test_job.run_id))
        assert elb_context.elt_run_dir == Path(expected_path)


class TestELBContextBuilder:
    @pytest.fixture
    def target_postgres(self, project_add_service):
        try:
            return project_add_service.add(PluginType.LOADERS, "target-postgres")
        except PluginAlreadyAddedException as err:
            return err.plugin

    def test_builder_returns_elb_context(
        self, project, session, project_plugins_service, tap, target
    ):
        """Ensure that builder is returning ELBContext and not itself."""
        builder = ELBContextBuilder(
            project=project,
            plugins_service=project_plugins_service,
            job=None,
        )
        builder.session = session

        assert isinstance(builder.context(), ELBContext)
        assert isinstance(builder.make_block(tap).invoker.context, ELBContext)

    def test_make_block_returns_valid_singer_block(
        self, project, session, project_plugins_service, tap, target
    ):
        """Ensure that calling make_block returns a valid SingerBlock."""
        builder = ELBContextBuilder(
            project=project,
            plugins_service=project_plugins_service,
            job=None,
        )
        builder.session = session

        block = builder.make_block(tap)
        assert block.string_id == tap.name
        assert block.producer
        assert not block.consumer

        block = builder.make_block(target)
        assert block.string_id == target.name
        assert block.consumer
        assert not block.producer

    def test_make_block_tracks_envs(
        self, project, session, project_plugins_service, tap, target
    ):
        """Ensure that calling make_block correctly stacks env vars."""
        builder = ELBContextBuilder(
            project=project,
            plugins_service=project_plugins_service,
            job=None,
        )
        builder.session = session

        block = builder.make_block(tap)
        assert block.string_id == tap.name
        initial_dict = builder._env.copy()

        block2 = builder.make_block(target)
        assert block2.string_id == target.name
        assert initial_dict.items() <= builder._env.items()
        assert builder._env.items() >= block.context.env.items()
        assert builder._env.items() >= block2.context.env.items()

    @pytest.mark.asyncio
    async def test_validate_envs(
        self, project, session, project_plugins_service, tap, target_postgres
    ):
        """Ensure that expected environment variables are present."""
        builder = ELBContextBuilder(
            project=project,
            plugins_service=project_plugins_service,
            job=None,
        )
        builder.session = session

        block = builder.make_block(tap)
        assert block.string_id == tap.name
        assert block.producer
        assert not block.consumer

        async with block.invoker.prepared(session):
            tap_env = block.invoker.env()

        assert tap_env["MELTANO_EXTRACTOR_NAME"] == tap.name
        assert tap_env["MELTANO_EXTRACTOR_NAMESPACE"] == tap.namespace
        assert tap_env["MELTANO_EXTRACTOR_VARIANT"] == tap.variant

        block = builder.make_block(target_postgres)
        assert block.string_id == target_postgres.name
        assert block.consumer
        assert not block.producer

        async with block.invoker.prepared(session):
            target_env = block.invoker.env()

        assert target_env["MELTANO_LOADER_NAME"] == target_postgres.name
        assert target_env["MELTANO_LOADER_NAMESPACE"] == target_postgres.namespace
        assert target_env["MELTANO_LOADER_VARIANT"] == target_postgres.variant

        assert target_env["MELTANO_LOAD_HOST"] == os.getenv(
            "TARGET_POSTGRES_HOST", "localhost"
        )

        assert (
            target_env["MELTANO_LOAD_DEFAULT_TARGET_SCHEMA"]
            == target_env["MELTANO_EXTRACT__LOAD_SCHEMA"]
            == target_env["MELTANO_EXTRACTOR_NAMESPACE"]
        )


class TestExtractLoadBlocks:
    @pytest.fixture
    def log_level_debug(self):
        root_logger = logging.getLogger()
        log_level = root_logger.level
        try:
            root_logger.setLevel(logging.DEBUG)
            yield
        finally:
            root_logger.setLevel(log_level)

    @pytest.fixture
    def log(self, tmp_path: Path):
        return tempfile.NamedTemporaryFile(mode="w+", dir=tmp_path)

    @pytest.fixture
    def tap_config_dir(self, tmp_path: Path, tap) -> Path:
        create_plugin_files(tmp_path, tap)
        return tmp_path

    @pytest.fixture
    def mapper_config_dir(self, tmp_path: Path, tap) -> Path:
        create_plugin_files(tmp_path, tap)
        return tmp_path

    @pytest.fixture
    def target_config_dir(self, tmp_path: Path, target) -> Path:
        create_plugin_files(tmp_path, target)
        return tmp_path

    @pytest.fixture
    def subject(self, session, elb_context):
        Job(
            job_name=TEST_STATE_ID,
            state=State.SUCCESS,
            payload_flags=Payload.STATE,
            payload={"singer_state": {"bookmarks": []}},
        ).save(session)

        return SingerRunner(elb_context)

    @pytest.fixture
    def process_mock_factory(self):
        def _factory(name):
            process_mock = mock.Mock()
            process_mock.name = name
            process_mock.wait = AsyncMock(return_value=0)
            return process_mock

        return _factory

    @pytest.fixture
    def tap_process(self, process_mock_factory, tap):
        tap = process_mock_factory(tap)
        tap.stdout.readline = AsyncMock(return_value="{}")  # noqa: P103
        tap.wait = AsyncMock(return_value=0)
        return tap

    @pytest.fixture
    def mapper_process(self, process_mock_factory, mapper):
        mapper = process_mock_factory(mapper)
        mapper.stdout.readline = AsyncMock(return_value="{}")  # noqa: P103
        mapper.wait = AsyncMock(return_value=0)
        return mapper

    @pytest.fixture
    def target_process(self, process_mock_factory, target):
        target = process_mock_factory(target)
        target.stdout.readline = AsyncMock(return_value="{}")  # noqa: P103
        target.wait = AsyncMock(return_value=0)
        return target

    @pytest.mark.asyncio
    async def test_link_io(  # noqa: WPS210
        self,
        session,
        subject,
        tap_config_dir,
        target_config_dir,
        mapper_config_dir,
        tap,
        target,
        mapper,
        tap_process,
        target_process,
        mapper_process,
        plugin_invoker_factory,
        elb_context,
        log,
        log_level_debug,
    ):
        tap_process.sterr.at_eof.side_effect = True
        tap_process.stdout.at_eof.side_effect = (False, False, True)
        tap_process.stdout.readline = AsyncMock(
            side_effect=(
                b"%b" % json.dumps({"key": "value"}).encode(),
                b"%b" % MOCK_RECORD_MESSAGE.encode(),
            )
        )

        mapper_process.sterr.at_eof.side_effect = True
        mapper_process.stdout.at_eof.side_effect = (False, False, True)
        mapper_process.stdout.readline = AsyncMock(
            side_effect=(
                b"%b" % json.dumps({"key": "mapper-mocked-value"}).encode(),
                b"%b" % MOCK_RECORD_MESSAGE.encode(),
            )
        )

        tap_invoker = plugin_invoker_factory(tap, config_dir=tap_config_dir)
        mapper_invoker = plugin_invoker_factory(mapper, config_dir=mapper_config_dir)
        target_invoker = plugin_invoker_factory(target, config_dir=target_config_dir)

        invoke_async = AsyncMock(
            side_effect=(tap_process, mapper_process, target_process)
        )
        with mock.patch.object(PluginInvoker, "invoke_async", new=invoke_async):
            blocks = (
                SingerBlock(
                    block_ctx=elb_context,
                    project=elb_context.project,
                    plugins_service=elb_context.plugins_service,
                    plugin_invoker=tap_invoker,
                    plugin_args=[],
                ),
                SingerBlock(
                    block_ctx=elb_context,
                    project=elb_context.project,
                    plugins_service=elb_context.plugins_service,
                    plugin_invoker=mapper_invoker,
                    plugin_args=[],
                ),
                SingerBlock(
                    block_ctx=elb_context,
                    project=elb_context.project,
                    plugins_service=elb_context.plugins_service,
                    plugin_invoker=target_invoker,
                    plugin_args=[],
                ),
            )

            elb = ExtractLoadBlocks(elb_context, blocks)
            elb.validate_set()

            for block in elb.blocks:
                await block.pre(elb.context)
                await block.start()

            await elb._link_io()

            # explicitly check the counts of each block's output to ensure they are linked
            # count is going to be logger + 1 for next blocks stdin
            assert len(elb.blocks[0].outputs) == 2

            # block0 should write output to block1 stdin
            assert elb.blocks[1].stdin in elb.blocks[0].outputs

            assert len(elb.blocks[2].outputs) == 1  # logger only
            # block1 should write output to block2 stdin
            assert elb.blocks[2].stdin in elb.blocks[1].outputs

            # block2 should write output to logger and no where else
            assert len(elb.blocks[2].outputs) == 1

    @pytest.mark.asyncio
    async def test_extract_load_block(
        self,
        session,
        subject,
        tap_config_dir,
        target_config_dir,
        mapper_config_dir,
        tap,
        target,
        mapper,
        tap_process,
        target_process,
        mapper_process,
        plugin_invoker_factory,
        elb_context,
        log,
    ):
        tap_process.sterr.at_eof.side_effect = True
        tap_process.stdout.at_eof.side_effect = (False, False, True)
        tap_process.stdout.readline = AsyncMock(
            side_effect=(
                b"%b" % json.dumps({"key": "value"}).encode(),
                b"%b" % MOCK_RECORD_MESSAGE.encode(),
            )
        )

        mapper_process.sterr.at_eof.side_effect = True
        mapper_process.stdout.at_eof.side_effect = (False, False, True)
        mapper_process.stdout.readline = AsyncMock(
            side_effect=(
                b"%b" % json.dumps({"key": "mapper-value"}).encode(),
                b"%b" % MOCK_RECORD_MESSAGE.encode(),
            )
        )

        tap_invoker = plugin_invoker_factory(tap, config_dir=tap_config_dir)
        mapper_invoker = plugin_invoker_factory(mapper, config_dir=mapper_config_dir)
        target_invoker = plugin_invoker_factory(target, config_dir=target_config_dir)

        invoke_async = AsyncMock(
            side_effect=(tap_process, mapper_process, target_process)
        )
        with mock.patch.object(PluginInvoker, "invoke_async", new=invoke_async):
            blocks = (
                SingerBlock(
                    block_ctx=elb_context,
                    project=elb_context.project,
                    plugins_service=elb_context.plugins_service,
                    plugin_invoker=tap_invoker,
                    plugin_args=[],
                ),
                SingerBlock(
                    block_ctx=elb_context,
                    project=elb_context.project,
                    plugins_service=elb_context.plugins_service,
                    plugin_invoker=mapper_invoker,
                    plugin_args=[],
                ),
                SingerBlock(
                    block_ctx=elb_context,
                    project=elb_context.project,
                    plugins_service=elb_context.plugins_service,
                    plugin_invoker=target_invoker,
                    plugin_args=[],
                ),
            )

            elb = ExtractLoadBlocks(elb_context, blocks)
            elb.validate_set()
            await elb.run()

            assert tap_process.wait.called
            assert tap_process.stdout.readline.called

            assert mapper_process.wait.called
            assert mapper_process.stdout.readline.called
            assert mapper_process.stdin.writeline.called

            assert target_process.wait.called
            assert target_process.stdin.writeline.called

            # sanity check to verify that we saw mapper output and not tap output
            first_write = target_process.stdin.writeline.call_args_list[0]
            assert "mapper" in first_write[0][0]

    @pytest.mark.asyncio
    async def test_elb_validation(
        self,
        session,
        subject,
        tap_config_dir,
        target_config_dir,
        tap,
        target,
        tap_process,
        target_process,
        plugin_invoker_factory,
        elb_context,
    ):

        tap_process.sterr.at_eof.side_effect = True
        tap_process.stdout.at_eof.side_effect = (False, False, True)
        tap_process.stdout.readline = AsyncMock(
            side_effect=(
                b"%b" % json.dumps({"key": "value"}).encode(),
                b"%b" % MOCK_RECORD_MESSAGE.encode(),
            )
        )

        tap_invoker = plugin_invoker_factory(tap, config_dir=tap_config_dir)
        target_invoker = plugin_invoker_factory(target, config_dir=target_config_dir)

        invoke_async = AsyncMock(side_effect=(tap_process, target_process))
        with mock.patch.object(PluginInvoker, "invoke_async", new=invoke_async):

            blocks = (
                SingerBlock(
                    block_ctx=elb_context,
                    project=elb_context.project,
                    plugins_service=elb_context.plugins_service,
                    plugin_invoker=tap_invoker,
                    plugin_args=[],
                ),
            )

            elb = ExtractLoadBlocks(elb_context, blocks)

            with pytest.raises(
                BlockSetValidationError,
                match="^.*: last block in set should not be a producer",
            ):
                elb.validate_set()

            blocks = (
                SingerBlock(
                    block_ctx=elb_context,
                    project=elb_context.project,
                    plugins_service=elb_context.plugins_service,
                    plugin_invoker=target_invoker,
                    plugin_args=[],
                ),
                SingerBlock(
                    block_ctx=elb_context,
                    project=elb_context.project,
                    plugins_service=elb_context.plugins_service,
                    plugin_invoker=tap_invoker,
                    plugin_args=[],
                ),
            )
            elb = ExtractLoadBlocks(elb_context, blocks)
            with pytest.raises(
                BlockSetValidationError,
                match="^.*: first block in set should not be consumer",
            ):
                elb.validate_set()

            blocks = (
                SingerBlock(
                    block_ctx=elb_context,
                    project=elb_context.project,
                    plugins_service=elb_context.plugins_service,
                    plugin_invoker=tap_invoker,
                    plugin_args=[],
                ),
                SingerBlock(
                    block_ctx=elb_context,
                    project=elb_context.project,
                    plugins_service=elb_context.plugins_service,
                    plugin_invoker=tap_invoker,
                    plugin_args=[],
                ),
                SingerBlock(
                    block_ctx=elb_context,
                    project=elb_context.project,
                    plugins_service=elb_context.plugins_service,
                    plugin_invoker=target_invoker,
                    plugin_args=[],
                ),
            )
            elb = ExtractLoadBlocks(elb_context, blocks)
            with pytest.raises(
                BlockSetValidationError,
                match="^.*: intermediate blocks must be producers AND consumers",
            ):
                elb.validate_set()

    @pytest.mark.asyncio
    async def test_elb_with_job_context(
        self,
        session,
        subject,
        tap_config_dir,
        mapper_config_dir,
        target_config_dir,
        tap,
        mapper,
        target,
        tap_process,
        mapper_process,
        target_process,
        plugin_invoker_factory,
        elb_context,
        project,
    ):
        tap_process.sterr.at_eof.side_effect = True
        tap_process.stdout.at_eof.side_effect = (False, False, True)
        tap_process.stdout.readline = AsyncMock(
            side_effect=(
                b"%b" % json.dumps({"key": "value"}).encode(),
                b"%b" % MOCK_RECORD_MESSAGE.encode(),
            )
        )

        mapper_process.sterr.at_eof.side_effect = True
        mapper_process.stdout.at_eof.side_effect = (False, False, True)
        mapper_process.stdout.readline = AsyncMock(
            side_effect=(
                b"%b" % json.dumps({"key": "mapper-value"}).encode(),
                b"%b" % MOCK_RECORD_MESSAGE.encode(),
            )
        )

        tap_invoker = plugin_invoker_factory(tap, config_dir=tap_config_dir)
        mapper_invoker = plugin_invoker_factory(mapper, config_dir=mapper_config_dir)
        target_invoker = plugin_invoker_factory(target, config_dir=target_config_dir)

        project.active_environment = Environment(name="test")

        invoke_async = AsyncMock(
            side_effect=(tap_process, mapper_process, target_process)
        )
        with mock.patch.object(PluginInvoker, "invoke_async", new=invoke_async):
            blocks = (
                SingerBlock(
                    block_ctx=elb_context,
                    project=elb_context.project,
                    plugins_service=elb_context.plugins_service,
                    plugin_invoker=tap_invoker,
                    plugin_args=[],
                ),
                SingerBlock(
                    block_ctx=elb_context,
                    project=elb_context.project,
                    plugins_service=elb_context.plugins_service,
                    plugin_invoker=mapper_invoker,
                    plugin_args=[],
                ),
                SingerBlock(
                    block_ctx=elb_context,
                    project=elb_context.project,
                    plugins_service=elb_context.plugins_service,
                    plugin_invoker=target_invoker,
                    plugin_args=[],
                ),
            )

            elb = ExtractLoadBlocks(elb_context, blocks)
            elb.validate_set()

            assert elb.context.job.job_name == "test:tap-mock-to-target-mock"

            # just to be sure, we'll double-check the state_id is the same for each block
            for block in blocks:
                assert block.context.job.job_name == "test:tap-mock-to-target-mock"

            elb.run_with_job = AsyncMock()

            await elb.run()
            assert elb.run_with_job.call_count == 1


class TestExtractLoadUtils:
    def test_generate_state_id(self):
        """Verify that a state ID is generated correctly given an active environment and optional suffix."""
        block1 = mock.Mock(spec=IOBlock)
        block1.string_id = "block1"

        block2 = mock.Mock(spec=IOBlock)
        block2.string_id = "block2"

        project = mock.Mock()
        project.active_environment = Environment(name="test")

        assert (
            generate_state_id(project, None, block1, block2) == "test:block1-to-block2"
        )

        assert (
            generate_state_id(project, "suffix", block1, block2)
            == "test:block1-to-block2:suffix"
        )

    def test_generate_state_id_no_environment(self):
        """Verify an error is raised when attempting to generate a state ID with no active environment."""
        block1 = mock.Mock(spec=IOBlock)
        block1.string_id = "block1"

        block2 = mock.Mock(spec=IOBlock)
        block2.string_id = "block2"

        project = mock.Mock()
        project.active_environment = None

        with pytest.raises(RunnerError):
            generate_state_id(project, None, block1, block2)

    def test_generate_state_id_component_contains_delimiter(self):
        """Verify an error is raised when attempting to generate a state ID with a component that contains the defined delimiter string."""
        block1 = mock.Mock(spec=IOBlock)
        block1.string_id = "block1"

        block2 = mock.Mock(spec=IOBlock)
        block2.string_id = "block2"

        project = mock.Mock()
        project.active_environment = Environment(name="test")

        with pytest.raises(RunnerError):
            generate_state_id(project, STATE_ID_COMPONENT_DELIMITER, block1, block2)
