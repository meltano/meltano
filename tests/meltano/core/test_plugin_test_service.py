from __future__ import annotations

import asyncio
import json
import sys
import typing as t
from uuid import uuid4

import pytest
from mock import patch

from meltano.core.plugin.error import PluginNotSupportedError
from meltano.core.plugin_test_service import (
    ExtractorTestService,
    PluginTestServiceFactory,
)

if t.TYPE_CHECKING:
    from meltano.core.plugin.project_plugin import ProjectPlugin


def generate_record_message():
    return json.dumps({"type": "RECORD", "record": {"id": str(uuid4())}})


MOCK_STATE_MESSAGE = json.dumps({"type": "STATE"})
MOCK_RECORD_MESSAGE = generate_record_message()


class TestPluginTestServiceFactory:
    @pytest.fixture(autouse=True)
    @patch("meltano.core.plugin_invoker.PluginInvoker")
    def setup(self, mock_invoker):
        self.mock_invoker = mock_invoker

    def test_extractor_plugin(self, tap: ProjectPlugin):
        self.mock_invoker.plugin = tap

        test_service = PluginTestServiceFactory(self.mock_invoker).get_test_service()
        assert isinstance(test_service, ExtractorTestService)

    def test_loader_plugin(self, target: ProjectPlugin):
        self.mock_invoker.plugin = target

        with pytest.raises(
            PluginNotSupportedError,
            match=(
                f"Operation not supported for {target.type.descriptor} {target.name!r}"
            ),
        ):
            PluginTestServiceFactory(self.mock_invoker).get_test_service()


def mock_invoke_async(*lines: str, err: str | None = None):
    statements = [f"print('{line}')" for line in lines]

    if err:
        statements.append(f"exit('{err}')")

    def invoke_async(**kwargs):
        return asyncio.create_subprocess_exec(
            sys.executable,
            "-c",
            "; ".join(statements),
            **kwargs,
        )

    return invoke_async


@patch("meltano.core.plugin_invoker.PluginInvoker")
class TestExtractorTestService:
    @pytest.mark.asyncio()
    async def test_validate_success(self, mock_invoker):
        mock_invoker.invoke_async = mock_invoke_async(MOCK_RECORD_MESSAGE)

        is_valid, detail = await ExtractorTestService(mock_invoker).validate()

        assert is_valid
        assert detail == MOCK_RECORD_MESSAGE

    @pytest.mark.asyncio()
    async def test_validate_success_ignore_non_json(self, mock_invoker):
        mock_invoker.invoke_async = mock_invoke_async(
            "Not JSON",
            MOCK_RECORD_MESSAGE,
        )

        is_valid, detail = await ExtractorTestService(mock_invoker).validate()

        assert is_valid
        assert detail == MOCK_RECORD_MESSAGE

    @pytest.mark.asyncio()
    async def test_validate_success_ignore_non_record_msg(self, mock_invoker):
        mock_invoker.invoke_async = mock_invoke_async(
            MOCK_STATE_MESSAGE,
            MOCK_RECORD_MESSAGE,
        )

        is_valid, detail = await ExtractorTestService(mock_invoker).validate()

        assert is_valid
        assert detail == MOCK_RECORD_MESSAGE

    @pytest.mark.asyncio()
    async def test_validate_success_stop_after_record_msg(self, mock_invoker):
        mock_invoker.invoke_async = mock_invoke_async(
            MOCK_STATE_MESSAGE,
            MOCK_RECORD_MESSAGE,
            generate_record_message(),
        )

        is_valid, detail = await ExtractorTestService(mock_invoker).validate()

        assert is_valid
        assert detail == MOCK_RECORD_MESSAGE

    @pytest.mark.asyncio()
    async def test_validate_failure_no_record_msg(self, mock_invoker):
        mock_invoker.invoke_async = mock_invoke_async(MOCK_STATE_MESSAGE)

        is_valid, detail = await ExtractorTestService(mock_invoker).validate()

        assert not is_valid
        assert "No RECORD message received" in detail

    @pytest.mark.asyncio()
    async def test_validate_failure_subprocess_err(self, mock_invoker):
        mock_invoker.invoke_async = mock_invoke_async(
            MOCK_STATE_MESSAGE,
            err="A subprocess error occurred",
        )

        is_valid, detail = await ExtractorTestService(mock_invoker).validate()

        assert not is_valid
        assert "A subprocess error occurred" in detail

    @pytest.mark.asyncio()
    async def test_validate_failure_plugin_invoke_exception(self, mock_invoker):
        mock_exception = Exception("An exception occurred on plugin invocation")
        mock_invoker.invoke_async.side_effect = mock_exception

        is_valid, detail = await ExtractorTestService(mock_invoker).validate()

        assert not is_valid
        assert str(mock_exception) in detail
