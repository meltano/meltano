from __future__ import annotations

import asyncio
import tempfile

import mock
import pytest
import structlog
from mock import AsyncMock, Mock
from structlog.testing import capture_logs

from meltano.core.block.singer import SingerBlock
from meltano.core.job import Job
from meltano.core.logging import OutputLogger


class TestSingerBlocks:
    @pytest.fixture
    def log(self, tmp_path):
        return tempfile.NamedTemporaryFile(mode="w+", dir=tmp_path)

    @pytest.fixture()
    def elt_context(self, project, session, tap, target, elt_context_builder):
        job = Job(job_name="pytest_test_runner")

        return (
            elt_context_builder.with_session(session)
            .with_extractor(tap.name)
            .with_job(job)
            .with_loader(target.name)
            .context()
        )

    @pytest.fixture()
    def process_mock_factory(self):
        def _factory(name):
            process_mock = Mock()
            process_mock.name = name
            process_mock.wait = AsyncMock(return_value=0)
            return process_mock

        return _factory

    @pytest.fixture()
    def mock_tap_plugin_invoker(self, process_mock_factory, tap):
        stdout_lines = (b"out1\n", b"out2\n", b"out3\n")
        stderr_lines = (b"err1\n", b"err2\n", b"err3\n")

        tap_process = process_mock_factory(tap)
        tap_process.stdout = mock.MagicMock()
        tap_process.stdout.at_eof.side_effect = (False, False, False, True)
        tap_process.stdout.readline = AsyncMock(side_effect=stdout_lines)
        tap_process.stderr = mock.MagicMock()
        tap_process.stderr.at_eof.side_effect = (False, False, False, True)
        tap_process.stderr.readline = AsyncMock(side_effect=stderr_lines)

        tap_process.stdin = mock.MagicMock()
        tap_process.stdin.wait_closed = AsyncMock(return_value=True)

        tap_process.wait = AsyncMock(return_value=0)

        invoker = Mock()
        invoker.invoke_async = AsyncMock(return_value=tap_process)
        invoker.plugin = tap
        invoker.cleanup = AsyncMock()
        return invoker

    @pytest.fixture()
    def mock_target_plugin_invoker(self, process_mock_factory, target):
        target_process = process_mock_factory(target)
        target_process.stdin = mock.MagicMock()
        target_process.stdin.wait_closed = AsyncMock(return_value=True)

        invoker = Mock()
        invoker.invoke_async = AsyncMock(return_value=target_process)
        invoker.plugin = target
        invoker.cleanup = AsyncMock()
        return invoker

    @pytest.mark.asyncio
    async def test_singer_block_start(
        self, elt_context, mock_tap_plugin_invoker, mock_target_plugin_invoker
    ):

        block = SingerBlock(
            block_ctx=elt_context,
            project=elt_context.project,
            plugins_service=elt_context.plugins_service,
            plugin_invoker=mock_tap_plugin_invoker,
            plugin_args={"foo": "bar"},
        )
        assert block.producer
        await block.start()
        assert mock_tap_plugin_invoker.invoke_async.called
        assert mock_tap_plugin_invoker.invoke_async.call_args[1]["stdin"] is None
        assert (
            mock_tap_plugin_invoker.invoke_async.call_args[1]["stdout"]
            == asyncio.subprocess.PIPE
        )
        assert (
            mock_tap_plugin_invoker.invoke_async.call_args[1]["stderr"]
            == asyncio.subprocess.PIPE
        )

        block = SingerBlock(
            block_ctx=elt_context,
            project=elt_context.project,
            plugins_service=elt_context.plugins_service,
            plugin_invoker=mock_target_plugin_invoker,
            plugin_args={"foo": "bar"},
        )
        assert block.consumer
        await block.start()
        assert mock_target_plugin_invoker.invoke_async.called
        assert (
            mock_target_plugin_invoker.invoke_async.call_args[1]["stdin"]
            == asyncio.subprocess.PIPE
        )
        assert (
            mock_target_plugin_invoker.invoke_async.call_args[1]["stdout"]
            == asyncio.subprocess.PIPE
        )
        assert (
            mock_target_plugin_invoker.invoke_async.call_args[1]["stderr"]
            == asyncio.subprocess.PIPE
        )

    @pytest.mark.asyncio
    async def test_singer_block_stop(self, elt_context, mock_target_plugin_invoker):
        block = SingerBlock(
            block_ctx=elt_context,
            project=elt_context.project,
            plugins_service=elt_context.plugins_service,
            plugin_invoker=mock_target_plugin_invoker,
            plugin_args={"foo": "bar"},
        )
        await block.start()

        await block.stop(True)
        assert block.process_handle.kill.called
        assert block.invoker.cleanup.called

        block = SingerBlock(
            block_ctx=elt_context,
            project=elt_context.project,
            plugins_service=elt_context.plugins_service,
            plugin_invoker=mock_target_plugin_invoker,
            plugin_args={"foo": "bar"},
        )
        await block.start()

        await block.stop(False)
        assert block.process_handle.terminate.called
        assert block.invoker.cleanup.called

    @pytest.mark.asyncio
    async def test_singer_block_io(self, elt_context, mock_tap_plugin_invoker, log):
        producer = SingerBlock(
            block_ctx=elt_context,
            project=elt_context.project,
            plugins_service=elt_context.plugins_service,
            plugin_invoker=mock_tap_plugin_invoker,
            plugin_args={"foo": "bar"},
        )

        mock_tap_plugin_invoker.output_handlers = (
            []
        )  # we're capturing logs below directly

        output_log = OutputLogger(log)
        log = structlog.getLogger("test")
        producer.stdout_link(output_log.out("stdout", log))
        producer.stderr_link(output_log.out("stderr", log))

        # This test is a great proxy for general io tests
        # if you link the output logger, you can use structlog's capture method
        # to capture the output and check output was actually consumed AND linked correctly.
        with capture_logs() as cap_logs:
            await producer.start()

            io_futures = [producer.proxy_stdout(), producer.proxy_stderr()]

            done, _ = await asyncio.wait(
                io_futures,
                return_when=asyncio.FIRST_COMPLETED,
            )

            expected_lines = [
                {"name": "stdout", "event": "out1", "log_level": "info"},
                {"name": "stdout", "event": "out2", "log_level": "info"},
                {"name": "stdout", "event": "out3", "log_level": "info"},
                {"name": "stderr", "event": "err1", "log_level": "info"},
                {"name": "stderr", "event": "err2", "log_level": "info"},
                {"name": "stderr", "event": "err3", "log_level": "info"},
            ]

            assert cap_logs == expected_lines

    @pytest.mark.asyncio
    async def test_singer_block_close_stdin(
        self, elt_context, mock_tap_plugin_invoker, mock_target_plugin_invoker
    ):

        producer = SingerBlock(
            block_ctx=elt_context,
            project=elt_context.project,
            plugins_service=elt_context.plugins_service,
            plugin_invoker=mock_tap_plugin_invoker,
            plugin_args={"foo": "bar"},
        )
        assert producer.producer

        await producer.start()
        await producer.close_stdin()
        assert producer.process_handle.stdin.wait_closed.call_count == 0

        consumer = SingerBlock(
            block_ctx=elt_context,
            project=elt_context.project,
            plugins_service=elt_context.plugins_service,
            plugin_invoker=mock_target_plugin_invoker,
            plugin_args={"foo": "bar"},
        )
        assert consumer.consumer

        await consumer.start()
        await consumer.close_stdin()
        assert consumer.process_handle.stdin.wait_closed.call_count == 1
