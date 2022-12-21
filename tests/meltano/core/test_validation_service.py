from __future__ import annotations

import pytest
from mock import Mock

from meltano.core.plugin import PluginType
from meltano.core.project import Project
from meltano.core.validation_service import ValidationsRunner


class MockValidationsRunner(ValidationsRunner):
    async def run_test(self, name: str):
        return 1


class TestValidationsRunner:
    @pytest.mark.asyncio
    async def test_run_all(self, session, dbt, plugin_invoker_factory):
        invoker = plugin_invoker_factory(dbt)
        runner = MockValidationsRunner(
            invoker,
            {
                "test": True,
                "other-test": False,
                "skipped-test": False,
            },
        )
        assert await runner.run_all(session) == {"test": 1}

        runner.select_test("other-test")
        assert await runner.run_all(session) == {"test": 1, "other-test": 1}

        runner.select_all()
        assert await runner.run_all(session) == {
            "test": 1,
            "other-test": 1,
            "skipped-test": 1,
        }

        noop_runner = MockValidationsRunner(invoker, {})
        noop_runner.invoker = Mock()
        result = await noop_runner.run_all(session)
        assert not result
        assert noop_runner.invoker.call_count == 0

    @pytest.mark.order(after="test_run_all")
    def test_collect_tests(self, project: Project):
        collected = MockValidationsRunner.collect(project, select_all=False)

        assert collected["dbt"].invoker.plugin.type == PluginType.TRANSFORMERS
        assert "test" in collected["dbt"].tests_selection
        assert not collected["dbt"].tests_selection["test"]

        collected["dbt"].select_all()
        assert collected["dbt"].tests_selection["test"]
