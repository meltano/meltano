import pytest
from meltano.cli.validate import collect_tests
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.project import Project
from meltano.core.validation_service import ValidationsRunner


class MockValidator:
    def __init__(self, name, selected):
        """Create a mock validator."""
        self.name = name
        self.selected = selected

    async def run_async(self, invoker: PluginInvoker) -> int:
        return 1


class TestValidationsRunner:
    @pytest.mark.asyncio
    async def test_run_all(self, session, dbt, plugin_invoker_factory):
        invoker = plugin_invoker_factory(dbt)
        runner = ValidationsRunner(
            invoker,
            {
                "test": MockValidator("test", selected=True),
                "other-test": MockValidator("other-test", selected=False),
                "skipped-test": MockValidator("skipped-test", selected=False),
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

    def test_collect_tests(self, project: Project):
        collected = collect_tests(project, select_all=False)

        assert "test" in collected["dbt"].validators
        assert not collected["dbt"].validators["test"].selected

        collected["dbt"].select_all()
        assert collected["dbt"].validators["test"].selected
