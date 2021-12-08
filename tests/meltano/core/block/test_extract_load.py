import json
import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest
from asynctest import CoroutineMock, Mock
from meltano.core.block.blockset import BlockSetValidationError
from meltano.core.block.extract_load import ExtractLoadBlocks
from meltano.core.block.singer import SingerBlock
from meltano.core.job import Job, Payload, State
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


class TestExtractLoadBlocks:
    @pytest.fixture
    def log(self, tmp_path):
        return tempfile.NamedTemporaryFile(mode="w+", dir=tmp_path)

    @pytest.fixture()
    def elt_context(self, project, session, tap, target, elt_context_builder):
        job = Job(job_id="pytest_test_runner")

        return (
            elt_context_builder.with_session(session)
            .with_extractor(tap.name)
            .with_job(job)
            .with_loader(target.name)
            .context()
        )

    @pytest.fixture()
    def tap_config_dir(self, mkdtemp, elt_context):
        tap_config_dir = mkdtemp()
        create_plugin_files(tap_config_dir, elt_context.extractor.plugin)
        return tap_config_dir

    @pytest.fixture()
    def target_config_dir(self, mkdtemp, elt_context):
        target_config_dir = mkdtemp()
        create_plugin_files(target_config_dir, elt_context.loader.plugin)
        return target_config_dir

    @pytest.fixture()
    def subject(self, session, elt_context):
        Job(
            job_id=TEST_JOB_ID,
            state=State.SUCCESS,
            payload_flags=Payload.STATE,
            payload={"singer_state": {"bookmarks": []}},
        ).save(session)

        return SingerRunner(elt_context)

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
    def target_process(self, process_mock_factory, target):
        target = process_mock_factory(target)
        target.stdout.readline = CoroutineMock(return_value="{}")  # noqa: P103
        target.wait = CoroutineMock(return_value=0)
        return target

    @pytest.mark.asyncio
    async def test_extract_load_block(
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
        elt_context,
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

        tap_invoker = plugin_invoker_factory(tap, config_dir=tap_config_dir)
        target_invoker = plugin_invoker_factory(target, config_dir=target_config_dir)

        invoke_async = CoroutineMock(side_effect=(tap_process, target_process))
        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ) as invoke_async:

            blocks = (
                SingerBlock(
                    block_ctx=elt_context,
                    project=elt_context.project,
                    plugins_service=elt_context.plugins_service,
                    plugin_invoker=tap_invoker,
                    plugin_args=[],
                ),
                SingerBlock(
                    block_ctx=elt_context,
                    project=elt_context.project,
                    plugins_service=elt_context.plugins_service,
                    plugin_invoker=target_invoker,
                    plugin_args=[],
                ),
            )

            elb = ExtractLoadBlocks(elt_context, blocks)
            elb.validate_set()
            assert await elb.run(session)

            assert tap_process.wait.called
            assert tap_process.stdout.readline.called
            assert target_process.wait.called
            assert target_process.stdin.writeline.called

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
        elt_context,
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
                    block_ctx=elt_context,
                    project=elt_context.project,
                    plugins_service=elt_context.plugins_service,
                    plugin_invoker=tap_invoker,
                    plugin_args=[],
                ),
            )

            elb = ExtractLoadBlocks(elt_context, blocks)

            with pytest.raises(
                BlockSetValidationError,
                match=r"^.*: last block in set should not be a producer",
            ):
                elb.validate_set()

            blocks = (
                SingerBlock(
                    block_ctx=elt_context,
                    project=elt_context.project,
                    plugins_service=elt_context.plugins_service,
                    plugin_invoker=target_invoker,
                    plugin_args=[],
                ),
                SingerBlock(
                    block_ctx=elt_context,
                    project=elt_context.project,
                    plugins_service=elt_context.plugins_service,
                    plugin_invoker=tap_invoker,
                    plugin_args=[],
                ),
            )
            elb = ExtractLoadBlocks(elt_context, blocks)
            with pytest.raises(
                BlockSetValidationError,
                match=r"^.*: first block in set should not be consumer",
            ):
                elb.validate_set()

            blocks = (
                SingerBlock(
                    block_ctx=elt_context,
                    project=elt_context.project,
                    plugins_service=elt_context.plugins_service,
                    plugin_invoker=tap_invoker,
                    plugin_args=[],
                ),
                SingerBlock(
                    block_ctx=elt_context,
                    project=elt_context.project,
                    plugins_service=elt_context.plugins_service,
                    plugin_invoker=tap_invoker,
                    plugin_args=[],
                ),
                SingerBlock(
                    block_ctx=elt_context,
                    project=elt_context.project,
                    plugins_service=elt_context.plugins_service,
                    plugin_invoker=target_invoker,
                    plugin_args=[],
                ),
            )
            elb = ExtractLoadBlocks(elt_context, blocks)
            with pytest.raises(
                BlockSetValidationError,
                match=r"^.*: intermediate blocks must be producers AND consumers",
            ):
                elb.validate_set()
