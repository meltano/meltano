from __future__ import annotations

import pytest
from mock import AsyncMock

from meltano.core.block.plugin_command import plugin_command_invoker


class TestInvokerCommand:
    @pytest.mark.asyncio
    async def test_run_passes_command_args_when_required(
        self, project, session, project_plugins_service, dbt
    ):
        cmd = plugin_command_invoker(
            dbt,
            project,
            command="test",
        )

        start_mock = AsyncMock()
        cmd.start = start_mock

        await cmd._start()
        assert not cmd.start.call_args[0]

        cmd = plugin_command_invoker(
            dbt,
            project,
            command="test",
            command_args=["--foo", "--bar"],
        )

        start_mock = AsyncMock()
        cmd.start = start_mock

        await cmd._start()
        assert len(cmd.start.call_args[0]) == 1
        assert cmd.start.call_args[0][0] == ["--foo", "--bar"]
