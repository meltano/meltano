from __future__ import annotations

import json
import typing as t
from signal import SIGTERM
from unittest.mock import AsyncMock, Mock, patch

import pytest

from meltano.core.plugin.error import PluginNotSupportedError
from meltano.core.plugin_test_service import (
    ExtractorTestService,
    LoaderTestService,
    PluginTestServiceFactory,
)

if t.TYPE_CHECKING:
    from meltano.core.plugin.project_plugin import ProjectPlugin

MOCK_STATE_MESSAGE = json.dumps({"type": "STATE"})
MOCK_RECORD_MESSAGE = json.dumps({"type": "RECORD"})


class TestPluginTestServiceFactory:
    @pytest.fixture(autouse=True)
    @patch("meltano.core.plugin_invoker.PluginInvoker")
    def setup(self, mock_invoker) -> None:
        self.mock_invoker = mock_invoker

    def test_extractor_plugin(self, tap: ProjectPlugin) -> None:
        self.mock_invoker.plugin = tap

        test_service = PluginTestServiceFactory(self.mock_invoker).get_test_service()
        assert isinstance(test_service, ExtractorTestService)

    def test_loader_plugin(self, target: ProjectPlugin) -> None:
        self.mock_invoker.plugin = target

        test_service = PluginTestServiceFactory(self.mock_invoker).get_test_service()
        assert isinstance(test_service, LoaderTestService)

    @pytest.mark.xfail(
        reason="Mappers are not supported for testing",
        raises=PluginNotSupportedError,
        strict=True,
    )
    def test_mapper_plugin(self, mapper: ProjectPlugin) -> None:
        self.mock_invoker.plugin = mapper
        PluginTestServiceFactory(self.mock_invoker).get_test_service()


class TestExtractorTestService:
    @pytest.fixture(autouse=True)
    @patch("meltano.core.plugin_invoker.PluginInvoker")
    def setup(self, mock_invoker) -> None:
        self.mock_invoke = Mock()
        self.mock_invoke.name = "utility-mock"
        self.mock_invoke.wait = AsyncMock(return_value=-SIGTERM)
        self.mock_invoke.returncode = -SIGTERM
        self.mock_invoker = mock_invoker
        self.mock_invoker.invoke_async = AsyncMock(return_value=self.mock_invoke)

    @pytest.mark.asyncio
    async def test_validate_success(self) -> None:
        self.mock_invoke.stderr.at_eof.side_effect = True
        self.mock_invoke.stdout.at_eof.side_effect = (False, True)
        self.mock_invoke.stdout.readline = AsyncMock(
            return_value=b"%b" % MOCK_RECORD_MESSAGE.encode(),
        )

        is_valid, detail = await ExtractorTestService(self.mock_invoker).validate()

        assert is_valid
        assert detail == MOCK_RECORD_MESSAGE

    @pytest.mark.asyncio
    async def test_validate_success_ignore_non_json(self) -> None:
        self.mock_invoke.stderr.at_eof.side_effect = True
        self.mock_invoke.stdout.at_eof.side_effect = (False, False, True)
        self.mock_invoke.stdout.readline = AsyncMock(
            side_effect=(b"Not JSON", b"%b" % MOCK_RECORD_MESSAGE.encode()),
        )

        is_valid, detail = await ExtractorTestService(self.mock_invoker).validate()

        assert is_valid
        assert detail == MOCK_RECORD_MESSAGE

    @pytest.mark.asyncio
    async def test_validate_success_ignore_non_record_msg(self) -> None:
        self.mock_invoke.stderr.at_eof.side_effect = True
        self.mock_invoke.stdout.at_eof.side_effect = (False, False, True)
        self.mock_invoke.stdout.readline = AsyncMock(
            side_effect=(
                b"%b" % json.dumps({"key": "value"}).encode(),
                b"%b" % MOCK_RECORD_MESSAGE.encode(),
            ),
        )

        is_valid, detail = await ExtractorTestService(self.mock_invoker).validate()

        assert is_valid
        assert detail == MOCK_RECORD_MESSAGE

    @pytest.mark.asyncio
    async def test_validate_success_stop_after_record_msg(self) -> None:
        self.mock_invoke.stderr.at_eof.side_effect = True
        self.mock_invoke.stdout.at_eof.side_effect = (False, False, False, True)
        self.mock_invoke.stdout.readline = AsyncMock(
            side_effect=(
                b"%b" % MOCK_STATE_MESSAGE.encode(),
                b"%b" % MOCK_RECORD_MESSAGE.encode(),
                b"%b" % MOCK_RECORD_MESSAGE.encode(),
            ),
        )

        is_valid, detail = await ExtractorTestService(self.mock_invoker).validate()

        assert is_valid
        assert detail == MOCK_RECORD_MESSAGE

        assert self.mock_invoke.stdout.readline.call_count == 2

    @pytest.mark.asyncio
    async def test_validate_failure_no_record_msg(self) -> None:
        self.mock_invoke.stderr.at_eof.side_effect = True
        self.mock_invoke.stdout.at_eof.side_effect = (False, True)
        self.mock_invoke.stdout.readline = AsyncMock(
            return_value=(b"%b" % MOCK_STATE_MESSAGE.encode()),
        )

        self.mock_invoke.wait = AsyncMock(return_value=0)
        self.mock_invoke.returncode = 0

        is_valid, detail = await ExtractorTestService(self.mock_invoker).validate()

        assert not is_valid
        assert detail is not None
        assert "No RECORD or BATCH message received" in detail

    @pytest.mark.asyncio
    async def test_validate_failure_subprocess_err(self) -> None:
        self.mock_invoke.stderr.at_eof.side_effect = True
        self.mock_invoke.stdout.at_eof.side_effect = (False, False, True)
        self.mock_invoke.stdout.readline = AsyncMock(
            side_effect=(
                b"%b" % MOCK_STATE_MESSAGE.encode(),
                b"A subprocess error occurred",
            ),
        )

        self.mock_invoke.wait = AsyncMock(return_value=1)
        self.mock_invoke.returncode = 1

        is_valid, detail = await ExtractorTestService(self.mock_invoker).validate()

        assert not is_valid
        assert "A subprocess error occurred" in detail

    @pytest.mark.asyncio
    async def test_validate_failure_plugin_invoke_exception(self) -> None:
        mock_exception = Exception("An exception occurred on plugin invocation")
        self.mock_invoker.invoke_async.side_effect = mock_exception

        is_valid, detail = await ExtractorTestService(self.mock_invoker).validate()

        assert not is_valid
        assert str(mock_exception) in detail


class TestLoaderTestService:
    @pytest.fixture(autouse=True)
    @patch("meltano.core.plugin_invoker.PluginInvoker")
    def setup(self, mock_invoker) -> None:
        self.mock_invoke = Mock()
        self.mock_invoke.name = "target-mock"
        self.mock_invoke.wait = AsyncMock(return_value=0)
        self.mock_invoke.returncode = 0
        self.mock_invoker = mock_invoker
        self.mock_invoker.plugin.name = "target-mock"
        self.mock_invoker.capabilities = frozenset()
        self.mock_invoker.invoke_async = AsyncMock(return_value=self.mock_invoke)

    @pytest.mark.asyncio
    async def test_validate_success(self) -> None:
        self.mock_invoke.stdin = AsyncMock()
        self.mock_invoke.stdin.write = Mock()
        self.mock_invoke.stdin.drain = AsyncMock()
        self.mock_invoke.stdin.close = Mock()
        self.mock_invoke.stdin.wait_closed = AsyncMock()
        self.mock_invoke.stdout = AsyncMock()
        self.mock_invoke.stdout.at_eof = Mock(side_effect=[False, True])
        self.mock_invoke.stdout.readline = AsyncMock(
            return_value=b"Successfully processed records\n",
        )

        is_valid, detail = await LoaderTestService(self.mock_invoker).validate()

        assert is_valid
        assert "Successfully processed test data" in detail

    @pytest.mark.asyncio
    async def test_validate_with_activate_version_capability(self) -> None:
        self.mock_invoker.capabilities = frozenset(["activate-version"])
        self.mock_invoke.stdin = AsyncMock()
        self.mock_invoke.stdin.write = Mock()
        self.mock_invoke.stdin.drain = AsyncMock()
        self.mock_invoke.stdin.close = Mock()
        self.mock_invoke.stdin.wait_closed = AsyncMock()
        self.mock_invoke.stdout = AsyncMock()
        self.mock_invoke.stdout.at_eof = Mock(side_effect=[False, True])
        self.mock_invoke.stdout.readline = AsyncMock(
            return_value=b"Successfully processed records\n",
        )

        loader_service = LoaderTestService(self.mock_invoker)
        test_messages = loader_service._generate_test_messages("test_stream")

        # Should have 4 messages: SCHEMA, RECORD, STATE, ACTIVATE_VERSION
        assert len(test_messages) == 4
        assert json.loads(test_messages[0])["type"] == "SCHEMA"
        assert json.loads(test_messages[1])["type"] == "RECORD"
        assert json.loads(test_messages[2])["type"] == "STATE"
        assert json.loads(test_messages[3])["type"] == "ACTIVATE_VERSION"

    @pytest.mark.asyncio
    async def test_validate_without_activate_version_capability(self) -> None:
        self.mock_invoker.capabilities = frozenset()
        self.mock_invoke.stdin = AsyncMock()
        self.mock_invoke.stdin.write = Mock()
        self.mock_invoke.stdin.drain = AsyncMock()
        self.mock_invoke.stdin.close = Mock()
        self.mock_invoke.stdin.wait_closed = AsyncMock()
        self.mock_invoke.stdout = AsyncMock()
        self.mock_invoke.stdout.at_eof = Mock(side_effect=[False, True])
        self.mock_invoke.stdout.readline = AsyncMock(
            return_value=b"Successfully processed records\n",
        )

        loader_service = LoaderTestService(self.mock_invoker)
        test_messages = loader_service._generate_test_messages("test_stream")

        # Should have 3 messages: SCHEMA, RECORD, STATE (no ACTIVATE_VERSION)
        assert len(test_messages) == 3
        assert json.loads(test_messages[0])["type"] == "SCHEMA"
        assert json.loads(test_messages[1])["type"] == "RECORD"
        assert json.loads(test_messages[2])["type"] == "STATE"

    @pytest.mark.asyncio
    async def test_validate_failure_non_zero_exit(self) -> None:
        self.mock_invoke.stdin = AsyncMock()
        self.mock_invoke.stdin.write = Mock()
        self.mock_invoke.stdin.drain = AsyncMock()
        self.mock_invoke.stdin.close = Mock()
        self.mock_invoke.stdin.wait_closed = AsyncMock()
        self.mock_invoke.stdout = AsyncMock()
        self.mock_invoke.stdout.at_eof = Mock(side_effect=[False, True])
        self.mock_invoke.stdout.readline = AsyncMock(
            return_value=b"Error processing records\n",
        )
        self.mock_invoke.wait = AsyncMock(return_value=1)
        self.mock_invoke.returncode = 1

        is_valid, detail = await LoaderTestService(self.mock_invoker).validate()

        assert not is_valid
        assert detail == "Error processing records"

    @pytest.mark.asyncio
    async def test_validate_failure_plugin_invoke_exception(self) -> None:
        mock_exception = Exception("An exception occurred on plugin invocation")
        self.mock_invoker.invoke_async.side_effect = mock_exception

        is_valid, detail = await LoaderTestService(self.mock_invoker).validate()

        assert not is_valid
        assert str(mock_exception) in detail

    @pytest.mark.asyncio
    async def test_validate_failure_during_message_write(self) -> None:
        self.mock_invoke.stdin = AsyncMock()
        self.mock_invoke.stdin.write = Mock(side_effect=BrokenPipeError("Pipe broken"))
        self.mock_invoke.stdin.drain = AsyncMock()
        self.mock_invoke.terminate = Mock()
        self.mock_invoke.wait = AsyncMock()

        is_valid, detail = await LoaderTestService(self.mock_invoker).validate()

        assert not is_valid
        assert "Pipe broken" in detail
        # Verify cleanup was called
        self.mock_invoke.terminate.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_with_empty_output_lines(self) -> None:
        self.mock_invoke.stdin = AsyncMock()
        self.mock_invoke.stdin.write = Mock()
        self.mock_invoke.stdin.drain = AsyncMock()
        self.mock_invoke.stdin.close = Mock()
        self.mock_invoke.stdin.wait_closed = AsyncMock()
        self.mock_invoke.stdout = AsyncMock()
        # Mix of empty and non-empty lines
        self.mock_invoke.stdout.at_eof = Mock(side_effect=[False, False, False, True])
        self.mock_invoke.stdout.readline = AsyncMock(
            side_effect=[b"\n", b"Processing...\n", b"\n"],
        )

        is_valid, detail = await LoaderTestService(self.mock_invoker).validate()

        assert is_valid
        assert "Successfully processed test data" in detail

    @pytest.mark.asyncio
    async def test_validate_with_error_in_output(self) -> None:
        self.mock_invoke.stdin = AsyncMock()
        self.mock_invoke.stdin.write = Mock()
        self.mock_invoke.stdin.drain = AsyncMock()
        self.mock_invoke.stdin.close = Mock()
        self.mock_invoke.stdin.wait_closed = AsyncMock()
        self.mock_invoke.stdout = AsyncMock()
        self.mock_invoke.stdout.at_eof = Mock(side_effect=[False, False, True])
        self.mock_invoke.stdout.readline = AsyncMock(
            side_effect=[b"Starting...\n", b"ERROR: Database connection failed\n"],
        )
        self.mock_invoke.wait = AsyncMock(return_value=0)
        self.mock_invoke.returncode = 0

        is_valid, detail = await LoaderTestService(self.mock_invoker).validate()

        # Even with return code 0, should fail because error was detected in output
        assert not is_valid
        assert detail == "ERROR: Database connection failed"
