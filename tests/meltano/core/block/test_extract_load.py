import json
import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest
from asynctest import CoroutineMock, Mock

from meltano.core.block.blockset import BlockSetValidationError
from meltano.core.block.extract_load import (
    ELBContext,
    ELBContextBuilder,
    ExtractLoadBlocks,
)
from meltano.core.block.singer import SingerBlock
from meltano.core.job import Job, Payload, State
from meltano.core.logging import OutputLogger
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.runner.singer import SingerRunner

TEST_JOB_ID = "test_job"
MOCK_STATE_MESSAGE = json.dumps({"type": "STATE"})
MOCK_RECORD_MESSAGE = json.dumps({"type": "RECORD"})


def create_plugin_files(config_dir: Path, plugin: ProjectPlugin):
    for file in plugin.config_files.values():
        Path(os.path.join(config_dir, file)).touch()

    return config_dir


@pytest.fixture
def test_job(session) -> Job:
    return Job(
        job_id=TEST_JOB_ID,
        state=State.SUCCESS,
        payload_flags=Payload.STATE,
        payload={"singer_state": {"bookmarks": []}},
    ).save(session)


@pytest.fixture
def output_logger() -> OutputLogger:
    return OutputLogger("test.log")


@pytest.fixture
def elb_context(project, session, test_job, output_logger) -> ELBContext:
    return ELBContext(
        project=project,
        session=session,
        job=test_job,
        base_output_logger=output_logger,
    )


class TestELBContext:
    def test_elt_run_dir_is_returned(self, project, test_job, elb_context: ELBContext):
        expected_path = project.job_dir(test_job.job_id, str(test_job.run_id))
        assert elb_context.elt_run_dir == Path(expected_path)


class TestELBContextBuilder:
    def test_builder_returns_elb_context(
        self, project, session, project_plugins_service, tap, target
    ):
        """Ensure that builder is returning ELBContext and not itself."""
        builder = ELBContextBuilder(
            project=project,
            plugins_service=project_plugins_service,
            session=session,
            job=None,
        )
        assert isinstance(builder.context(), ELBContext)
        assert isinstance(builder.make_block(tap).invoker.context, ELBContext)

    def test_make_block_returns_valid_singer_block(
        self, project, session, project_plugins_service, tap, target
    ):
        """Ensure that calling make_block returns a valid SingerBlock."""
        builder = ELBContextBuilder(
            project=project,
            plugins_service=project_plugins_service,
            session=session,
            job=None,
        )
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
            session=session,
            job=None,
        )
        block = builder.make_block(tap)
        assert block.string_id == tap.name
        initial_dict = builder._env.copy()

        block2 = builder.make_block(target)
        assert block2.string_id == target.name
        assert initial_dict.items() <= builder._env.items()
        assert builder._env.items() >= block.context.env.items()
        assert builder._env.items() >= block2.context.env.items()


class TestExtractLoadBlocks:
    @pytest.fixture
    def log(self, tmp_path):
        return tempfile.NamedTemporaryFile(mode="w+", dir=tmp_path)

    @pytest.fixture()
    def tap_config_dir(self, mkdtemp, tap):
        tap_config_dir = mkdtemp()
        create_plugin_files(tap_config_dir, tap)
        return tap_config_dir

    @pytest.fixture()
    def mapper_config_dir(self, mkdtemp, tap):
        mapper_config_dir = mkdtemp()
        create_plugin_files(mapper_config_dir, tap)
        return mapper_config_dir

    @pytest.fixture()
    def target_config_dir(self, mkdtemp, target):
        target_config_dir = mkdtemp()
        create_plugin_files(target_config_dir, target)
        return target_config_dir

    @pytest.fixture
    def subject(self, session, elb_context):
        Job(
            job_id=TEST_JOB_ID,
            state=State.SUCCESS,
            payload_flags=Payload.STATE,
            payload={"singer_state": {"bookmarks": []}},
        ).save(session)

        return SingerRunner(elb_context)

    @pytest.fixture()
    def process_mock_factory(self):
        def _factory(name):
            process_mock = Mock()
            process_mock.name = name
            process_mock.wait = CoroutineMock(return_value=0)
            return process_mock

        return _factory

    @pytest.fixture()
    def tap_process(self, process_mock_factory, tap):
        tap = process_mock_factory(tap)
        tap.stdout.readline = CoroutineMock(return_value="{}")  # noqa: P103
        tap.wait = CoroutineMock(return_value=0)
        return tap

    @pytest.fixture()
    def mapper_process(self, process_mock_factory, mapper):
        mapper = process_mock_factory(mapper)
        mapper.stdout.readline = CoroutineMock(return_value="{}")  # noqa: P103
        mapper.wait = CoroutineMock(return_value=0)
        return mapper

    @pytest.fixture()
    def target_process(self, process_mock_factory, target):
        target = process_mock_factory(target)
        target.stdout.readline = CoroutineMock(return_value="{}")  # noqa: P103
        target.wait = CoroutineMock(return_value=0)
        return target

    @pytest.mark.asyncio
    async def test_link_io(
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
        tap_process.stdout.readline = CoroutineMock(
            side_effect=(
                b"%b" % json.dumps({"key": "value"}).encode(),
                b"%b" % MOCK_RECORD_MESSAGE.encode(),
            )
        )

        mapper_process.sterr.at_eof.side_effect = True
        mapper_process.stdout.at_eof.side_effect = (False, False, True)
        mapper_process.stdout.readline = CoroutineMock(
            side_effect=(
                b"%b" % json.dumps({"key": "mapper-mocked-value"}).encode(),
                b"%b" % MOCK_RECORD_MESSAGE.encode(),
            )
        )

        tap_invoker = plugin_invoker_factory(tap, config_dir=tap_config_dir)
        mapper_invoker = plugin_invoker_factory(mapper, config_dir=mapper_config_dir)
        target_invoker = plugin_invoker_factory(target, config_dir=target_config_dir)

        invoke_async = CoroutineMock(
            side_effect=(tap_process, mapper_process, target_process)
        )
        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ) as invoke_async:
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
                await block.pre({"session": session})
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
        tap_process.stdout.readline = CoroutineMock(
            side_effect=(
                b"%b" % json.dumps({"key": "value"}).encode(),
                b"%b" % MOCK_RECORD_MESSAGE.encode(),
            )
        )

        mapper_process.sterr.at_eof.side_effect = True
        mapper_process.stdout.at_eof.side_effect = (False, False, True)
        mapper_process.stdout.readline = CoroutineMock(
            side_effect=(
                b"%b" % json.dumps({"key": "mapper-value"}).encode(),
                b"%b" % MOCK_RECORD_MESSAGE.encode(),
            )
        )

        tap_invoker = plugin_invoker_factory(tap, config_dir=tap_config_dir)
        mapper_invoker = plugin_invoker_factory(mapper, config_dir=mapper_config_dir)
        target_invoker = plugin_invoker_factory(target, config_dir=target_config_dir)

        invoke_async = CoroutineMock(
            side_effect=(tap_process, mapper_process, target_process)
        )
        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ) as invoke_async:

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
            assert await elb.run(session)

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
        tap_process.stdout.readline = CoroutineMock(
            side_effect=(
                b"%b" % json.dumps({"key": "value"}).encode(),
                b"%b" % MOCK_RECORD_MESSAGE.encode(),
            )
        )

        tap_invoker = plugin_invoker_factory(tap, config_dir=tap_config_dir)
        target_invoker = plugin_invoker_factory(target, config_dir=target_config_dir)

        invoke_async = CoroutineMock(side_effect=(tap_process, target_process))
        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ) as invoke_async:

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
                match=r"^.*: last block in set should not be a producer",
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
                match=r"^.*: first block in set should not be consumer",
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
                match=r"^.*: intermediate blocks must be producers AND consumers",
            ):
                elb.validate_set()

    @pytest.mark.asyncio
    async def test_elb_job_context(
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
    ):
        tap_process.sterr.at_eof.side_effect = True
        tap_process.stdout.at_eof.side_effect = (False, False, True)
        tap_process.stdout.readline = CoroutineMock(
            side_effect=(
                b"%b" % json.dumps({"key": "value"}).encode(),
                b"%b" % MOCK_RECORD_MESSAGE.encode(),
            )
        )

        mapper_process.sterr.at_eof.side_effect = True
        mapper_process.stdout.at_eof.side_effect = (False, False, True)
        mapper_process.stdout.readline = CoroutineMock(
            side_effect=(
                b"%b" % json.dumps({"key": "mapper-value"}).encode(),
                b"%b" % MOCK_RECORD_MESSAGE.encode(),
            )
        )

        tap_invoker = plugin_invoker_factory(tap, config_dir=tap_config_dir)
        mapper_invoker = plugin_invoker_factory(mapper, config_dir=mapper_config_dir)
        target_invoker = plugin_invoker_factory(target, config_dir=target_config_dir)

        invoke_async = CoroutineMock(
            side_effect=(tap_process, mapper_process, target_process)
        )
        with mock.patch.object(
                PluginInvoker, "invoke_async", new=invoke_async
        ) as invoke_async:
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

            assert elb.context.job.job_id == "tap-mock-target-mock"

            # just to be sure, we'll double check the job_id is the same for each block
            for block in blocks:
                assert block.context.job.job_id == "tap-mock-target-mock"

