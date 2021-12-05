import asyncio
import tempfile
from unittest import mock
from unittest.mock import AsyncMock

import pytest
import structlog
from asynctest import CoroutineMock, Mock
from meltano.core.block.singer import SingerBlock
from meltano.core.job import Job
from meltano.core.logging import OutputLogger
from structlog.testing import capture_logs


class TestSingerBlocks:
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
    def process_mock_factory(self):
        def _factory(name):
            process_mock = AsyncMock()
            process_mock.name = name
            process_mock.wait = CoroutineMock(return_value=0)
            return process_mock

        return _factory

    @pytest.fixture()
    def mock_tap_plugin_invoker(self, process_mock_factory, tap):
        stdout_lines = (b"out1\n", b"out2\n", b"out3\n")
        stderr_lines = (b"err1\n", b"err2\n", b"err3\n")

        tap_process = process_mock_factory(tap)
        tap_process.stdout = mock.MagicMock()
        tap_process.stdout.at_eof.side_effect = (False, False, False, True)
        tap_process.stdout.readline = CoroutineMock(side_effect=stdout_lines)
        tap_process.stderr = mock.MagicMock()
        tap_process.stderr.at_eof.side_effect = (False, False, False, True)
        tap_process.stderr.readline = CoroutineMock(side_effect=stderr_lines)

        tap_process.wait = CoroutineMock(return_value=0)

        invoker = Mock()
        invoker.invoke_async = CoroutineMock(return_value=tap_process)
        invoker.plugin = tap
        return invoker

    @pytest.fixture()
    def mock_target_plugin_invoker(self, process_mock_factory, target):
        target_process = process_mock_factory(target)
        target_process.stdin = mock.MagicMock()

        invoker = Mock()
        invoker.invoke_async = CoroutineMock(return_value=target_process)
        invoker.plugin = target
        return invoker

    @pytest.mark.asyncio
    async def test_singer_block_start(
        self, elt_context, mock_tap_plugin_invoker, mock_target_plugin_invoker
    ):

        block = SingerBlock(
            block_ctx=elt_context,
            plugin_invoker=mock_tap_plugin_invoker,
            plugin_args={"foo": "bar"},
        )
        assert block.producer
        await block.start()
        assert mock_tap_plugin_invoker.invoke_async.called
        assert mock_tap_plugin_invoker.invoke_async.call_args.kwargs["stdin"] is None
        assert (
            mock_tap_plugin_invoker.invoke_async.call_args.kwargs["stdout"]
            == asyncio.subprocess.PIPE
        )
        assert (
            mock_tap_plugin_invoker.invoke_async.call_args.kwargs["stderr"]
            == asyncio.subprocess.PIPE
        )

        block = SingerBlock(
            block_ctx=elt_context,
            plugin_invoker=mock_target_plugin_invoker,
            plugin_args={"foo": "bar"},
        )
        assert block.consumer
        await block.start()
        assert mock_target_plugin_invoker.invoke_async.called
        assert (
            mock_target_plugin_invoker.invoke_async.call_args.kwargs["stdin"]
            == asyncio.subprocess.PIPE
        )
        assert (
            mock_target_plugin_invoker.invoke_async.call_args.kwargs["stdout"]
            == asyncio.subprocess.PIPE
        )
        assert (
            mock_target_plugin_invoker.invoke_async.call_args.kwargs["stderr"]
            == asyncio.subprocess.PIPE
        )

    @pytest.mark.asyncio
    async def test_singer_block_stop(self, elt_context, mock_target_plugin_invoker):
        block = SingerBlock(
            block_ctx=elt_context,
            plugin_invoker=mock_target_plugin_invoker,
            plugin_args={"foo": "bar"},
        )
        await block.start()

        await block.stop(True)
        assert block.process_handle.kill.called
        assert block.invoker.cleanup.called

        block = SingerBlock(
            block_ctx=elt_context,
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
            plugin_invoker=mock_tap_plugin_invoker,
            plugin_args={"foo": "bar"},
        )

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
