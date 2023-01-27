from __future__ import annotations

import pytest

from meltano.core.plugin import PluginType


class TestSingerMapper:
    @pytest.fixture(scope="class")
    def subject(self, project_add_service):
        return project_add_service.add(PluginType.MAPPERS, "mapper-mock")

    @pytest.mark.asyncio
    async def test_exec_args(self, subject, session, plugin_invoker_factory):
        invoker = plugin_invoker_factory(subject)
        async with invoker.prepared(session):
            assert subject.exec_args(invoker) == ["--config", invoker.files["config"]]
