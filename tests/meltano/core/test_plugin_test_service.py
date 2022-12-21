from __future__ import annotations

import json

import pytest
from mock import AsyncMock, Mock, patch

from meltano.core.plugin.error import PluginNotSupportedError
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_test_service import (
    ExtractorTestService,
    PluginTestServiceFactory,
)

MOCK_STATE_MESSAGE = json.dumps({"type": "STATE"})
MOCK_RECORD_MESSAGE = json.dumps({"type": "RECORD"})


class TestPluginTestServiceFactory:
    @pytest.fixture(autouse=True)
    @patch("meltano.core.plugin_test_service.PluginInvoker")
    def setup(self, mock_invoker):
        self.mock_invoker = mock_invoker

    def test_extractor_plugin(self, tap: ProjectPlugin):
        self.mock_invoker.plugin = tap

        test_service = PluginTestServiceFactory(self.mock_invoker).get_test_service()
        assert isinstance(test_service, ExtractorTestService)

    def test_loader_plugin(self, target: ProjectPlugin):
        self.mock_invoker.plugin = target

        with pytest.raises(PluginNotSupportedError) as err:
            PluginTestServiceFactory(self.mock_invoker).get_test_service()
            assert (
                str(err.value)
                == f"Operation not supported for {target.type.descriptor} '{target.name}'"
            )


class TestExtractorTestService:
    @pytest.fixture(autouse=True)
    @patch("meltano.core.plugin_test_service.PluginInvoker")
    def setup(self, mock_invoker):
        self.mock_invoke = Mock()
        self.mock_invoke.name = "utility-mock"
        self.mock_invoke.wait = AsyncMock(return_value=-1)
        self.mock_invoke.returncode = -1
        self.mock_invoker = mock_invoker
        self.mock_invoker.invoke_async = AsyncMock(return_value=self.mock_invoke)

    @pytest.mark.asyncio
    async def test_validate_success(self):
        self.mock_invoke.sterr.at_eof.side_effect = True
        self.mock_invoke.stdout.at_eof.side_effect = (False, True)
        self.mock_invoke.stdout.readline = AsyncMock(
            return_value=b"%b" % MOCK_RECORD_MESSAGE.encode()
        )

        is_valid, detail = await ExtractorTestService(self.mock_invoker).validate()

        assert is_valid
        assert detail == MOCK_RECORD_MESSAGE

    @pytest.mark.asyncio
    async def test_validate_success_ignore_non_json(self):
        self.mock_invoke.sterr.at_eof.side_effect = True
        self.mock_invoke.stdout.at_eof.side_effect = (False, False, True)
        self.mock_invoke.stdout.readline = AsyncMock(
            side_effect=(b"Not JSON", b"%b" % MOCK_RECORD_MESSAGE.encode())
        )

        is_valid, detail = await ExtractorTestService(self.mock_invoker).validate()

        assert is_valid
        assert detail == MOCK_RECORD_MESSAGE

    @pytest.mark.asyncio
    async def test_validate_success_ignore_non_record_msg(self):
        self.mock_invoke.sterr.at_eof.side_effect = True
        self.mock_invoke.stdout.at_eof.side_effect = (False, False, True)
        self.mock_invoke.stdout.readline = AsyncMock(
            side_effect=(
                b"%b" % json.dumps({"key": "value"}).encode(),
                b"%b" % MOCK_RECORD_MESSAGE.encode(),
            )
        )

        is_valid, detail = await ExtractorTestService(self.mock_invoker).validate()

        assert is_valid
        assert detail == MOCK_RECORD_MESSAGE

    @pytest.mark.asyncio
    async def test_validate_success_stop_after_record_msg(self):
        self.mock_invoke.sterr.at_eof.side_effect = True
        self.mock_invoke.stdout.at_eof.side_effect = (False, False, False, True)
        self.mock_invoke.stdout.readline = AsyncMock(
            side_effect=(
                b"%b" % MOCK_STATE_MESSAGE.encode(),
                b"%b" % MOCK_RECORD_MESSAGE.encode(),
                b"%b" % MOCK_RECORD_MESSAGE.encode(),
            )
        )

        is_valid, detail = await ExtractorTestService(self.mock_invoker).validate()

        assert is_valid
        assert detail == MOCK_RECORD_MESSAGE

        assert self.mock_invoke.stdout.readline.call_count == 2

    @pytest.mark.asyncio
    async def test_validate_failure_no_record_msg(self):
        self.mock_invoke.sterr.at_eof.side_effect = True
        self.mock_invoke.stdout.at_eof.side_effect = (False, True)
        self.mock_invoke.stdout.readline = AsyncMock(
            return_value=(b"%b" % MOCK_STATE_MESSAGE.encode())
        )

        self.mock_invoke.wait = AsyncMock(return_value=0)
        self.mock_invoke.returncode = 0

        is_valid, detail = await ExtractorTestService(self.mock_invoker).validate()

        assert not is_valid
        assert "No RECORD message received" in detail

    @pytest.mark.asyncio
    async def test_validate_failure_subprocess_err(self):
        self.mock_invoke.sterr.at_eof.side_effect = True
        self.mock_invoke.stdout.at_eof.side_effect = (False, False, True)
        self.mock_invoke.stdout.readline = AsyncMock(
            side_effect=(
                b"%b" % MOCK_STATE_MESSAGE.encode(),
                b"A subprocess error occurred",
            )
        )

        self.mock_invoke.wait = AsyncMock(return_value=1)
        self.mock_invoke.returncode = 1

        is_valid, detail = await ExtractorTestService(self.mock_invoker).validate()

        assert not is_valid
        assert "A subprocess error occurred" in detail

    @pytest.mark.asyncio
    async def test_validate_failure_plugin_invoke_exception(self):
        mock_exception = Exception("An exception occurred on plugin invocation")
        self.mock_invoker.invoke_async.side_effect = mock_exception

        is_valid, detail = await ExtractorTestService(self.mock_invoker).validate()

        assert not is_valid
        assert str(mock_exception) in detail
