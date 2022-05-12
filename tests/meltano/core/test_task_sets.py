import pytest

from meltano.core.task_sets import TaskSets, tasks_from_str


class TestTaskSets:
    def test_tasks_from_str(self):

        cases = [
            ("generic", "tap target", TaskSets(name="generic", tasks=["tap target"])),
            (
                "single-list",
                "[tap target]",
                TaskSets(name="single-list", tasks=["tap target"]),
            ),
            (
                "multiple-lists",
                "[tap target, tap2 target2]",
                TaskSets(name="multiple-lists", tasks=["tap target", "tap2 target2"]),
            ),
            (
                "multiple-lists-with-spaces",
                "[tap target,  tap2 target2]",
                TaskSets(
                    name="multiple-lists-with-spaces",
                    tasks=["tap target", "tap2 target2"],
                ),
            ),
        ]

        for name, task_str, expected in cases:
            tset = tasks_from_str(name, task_str)
            assert tset.name == expected.name
            assert tset.tasks == expected.tasks

        obvious_edge_cases = [
            ("single-quoted-list", "'[tap target]'"),
            ("double-quoted-list", '"[tap target]"'),
            ("no-leading-bracket", "tap target]"),
            ("no-trailing-bracket", "[tap target"),
            ("comma-without-list", "tap target, tap2 target2"),
        ]

        for name, task_str in obvious_edge_cases:
            with pytest.raises(ValueError):
                tasks_from_str(name, task_str)
