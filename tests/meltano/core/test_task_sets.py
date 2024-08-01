from __future__ import annotations

import pytest

from meltano.core.task_sets import InvalidTasksError, TaskSets, tasks_from_yaml_str


class TestTaskSets:
    def test_squash(self) -> None:
        tset = TaskSets(name="test", tasks=["tap target", "tap2 target2"])
        assert tset._as_args() == ["tap", "target", "tap2", "target2"]

        tset = TaskSets(
            name="test",
            tasks=[["tap target"], ["some:cmd"], ["tap2 target2"]],
        )
        assert tset._as_args() == ["tap", "target", "some:cmd", "tap2", "target2"]

        tset = TaskSets(
            name="test",
            tasks=[["tap target", "some:cmd"], ["tap2 target2"]],
        )
        assert tset._as_args(preserve_top_level=True) == [
            ["tap", "target", "some:cmd"],
            ["tap2", "target2"],
        ]

    def test_tasks_from_yaml_str(self) -> None:
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
                "multiple-lists-quoted",
                "['tap target', 'tap2 target2']",
                TaskSets(
                    name="multiple-lists-quoted",
                    tasks=["tap target", "tap2 target2"],
                ),
            ),
            (
                "nested-mixed-lists",
                "[['tap target', 'tap2 target2'], 'cmd1']",
                TaskSets(
                    name="nested-mixed-lists",
                    tasks=[["tap target", "tap2 target2"], "cmd1"],
                ),
            ),
        ]

        for name, task_str, expected in cases:
            tset = tasks_from_yaml_str(name, task_str)
            assert tset.name == expected.name
            assert tset.tasks == expected.tasks

        obvious_edge_cases = [
            ("bad-yaml", "['tap target'"),
            ("too-many-levels", "[[['tap target']]]"),
            ("non-string-list", "['tap target', 5"),
        ]

        for name, task_str in obvious_edge_cases:
            with pytest.raises(InvalidTasksError):
                tasks_from_yaml_str(name, task_str)
