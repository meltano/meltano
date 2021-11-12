import asyncio
import json
import os
from asyncio import Task
from contextlib import AsyncExitStack
from pathlib import Path
from unittest import mock

import pytest
from asynctest import CoroutineMock, Mock
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


async def assert_pair_run(tap_block: SingerBlock, target_block: SingerBlock):
    """test a pair of blocks using a method similar to how singer runner/etl works today"""
    tap_process_future: Task = tap_block.process_future
    target_process_future: Task = target_block.process_future

    output_exception_future = asyncio.ensure_future(
        asyncio.wait(
            [
                tap_block.proxy_stdout(),
                tap_block.proxy_stderr(),
                target_block.proxy_stdout(),
                target_block.proxy_stderr(),
            ],
            return_when=asyncio.FIRST_EXCEPTION,
        ),
    )

    done, _ = await asyncio.wait(
        [tap_process_future, target_process_future, output_exception_future],
        return_when=asyncio.FIRST_COMPLETED,
    )

    # If `output_exception_future` completes first, one of the output handlers raised an exception or all completed successfully.
    if output_exception_future in done:
        output_futures_done, _ = output_exception_future.result()
        output_futures_failed = [
            future for future in output_futures_done if future.exception() is not None
        ]

        if output_futures_failed:
            raise output_futures_failed.pop().exception()
        else:
            # If all of the output handlers completed without raising an exception,
            # we still need to wait for the tap or target to complete.
            done, _ = await asyncio.wait(
                [tap_process_future],
                return_when=asyncio.FIRST_COMPLETED,
            )

    if target_process_future not in done:
        # If the tap completes before the target, the target should have a chance to process all tap output
        tap_code = tap_process_future.result()
        assert tap_code == 0

        # Wait for all buffered tap output to be processed
        await asyncio.wait([tap_block.proxy_stdout, tap_block.proxy_stderr])

    assert tap_process_future in done and target_process_future in done
    assert tap_process_future.result() == 0
    assert target_process_future.result() == 0


class TestBlock:
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
        tap.stdout.readline = CoroutineMock(return_value="{}")
        tap.wait = CoroutineMock(return_value=0)
        return tap

    @pytest.fixture()
    def target_process(self, process_mock_factory, target):
        target = process_mock_factory(target)
        target.stdout.readline = CoroutineMock(return_value="{}")
        target.wait = CoroutineMock(return_value=0)
        return target

    @pytest.mark.asyncio
    async def test_singer_block(
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
                SingerBlock(plugin_invoker=tap_invoker, plugin_args=[]),
                SingerBlock(plugin_invoker=target_invoker, plugin_args=[]),
            )

            async with AsyncExitStack() as stack:
                _ = [
                    await stack.enter_async_context(block.invoker.prepared(session))
                    for block in blocks
                ]
                for i, block in enumerate(blocks):
                    await block.start()
                    if block.requires_input:
                        if i != 0 and blocks[i - 1].has_output:
                            blocks[i - 1].stdout_link(
                                block.stdin
                            )  # link previous blocks stdout with current blocks stdin
                        else:
                            raise Exception(
                                "run step requires input but has no upstream"
                            )

            await assert_pair_run(blocks[0], blocks[1])

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
                SingerBlock(plugin_invoker=tap_invoker, plugin_args=[]),
                SingerBlock(plugin_invoker=target_invoker, plugin_args=[]),
            )

            elb = ExtractLoadBlocks(blocks)
            elb.validate_set()

            assert await elb.run(session)
            # await assert_pair_run(blocks[0], blocks[1])

            # await experimental_run(elb)

            # await assert_run(blocks[0], blocks[1])
            # assert tap_process.wait.called
            # assert tap_process.stdout.readline.called
            # await assert_run_exp(Span(blocks=blocks))
