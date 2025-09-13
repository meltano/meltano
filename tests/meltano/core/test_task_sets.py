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
            (
                "generic",
                "tap target",
                TaskSets(name="generic", tasks=["tap target"], env={}),
            ),
            (
                "single-list",
                "[tap target]",
                TaskSets(name="single-list", tasks=["tap target"], env={}),
            ),
            (
                "multiple-lists",
                "[tap target, tap2 target2]",
                TaskSets(
                    name="multiple-lists", tasks=["tap target", "tap2 target2"], env={}
                ),
            ),
            (
                "multiple-lists-quoted",
                "['tap target', 'tap2 target2']",
                TaskSets(
                    name="multiple-lists-quoted",
                    tasks=["tap target", "tap2 target2"],
                    env={},
                ),
            ),
            (
                "nested-mixed-lists",
                "[['tap target', 'tap2 target2'], 'cmd1']",
                TaskSets(
                    name="nested-mixed-lists",
                    tasks=[["tap target", "tap2 target2"], "cmd1"],
                    env={},
                ),
            ),
            # Test cases with environment variables
            (
                "with-env-vars",
                "{'tasks': ['tap target'], 'env': {'DBT_MODELS': '+gitlab+'}}",
                TaskSets(
                    name="with-env-vars",
                    tasks=["tap target"],
                    env={"DBT_MODELS": "+gitlab+"},
                ),
            ),
            (
                "with-env-null",
                "{'tasks': ['tap target'], 'env': null}",
                TaskSets(
                    name="with-env-null",
                    tasks=["tap target"],
                    env={},
                ),
            ),
            (
                "with-multiple-env-vars",
                (
                    "{'tasks': ['tap target'], "
                    "'env': {'DBT_MODELS': '+gitlab+', 'TARGET_BATCH_SIZE': '100'}}"
                ),
                TaskSets(
                    name="with-multiple-env-vars",
                    tasks=["tap target"],
                    env={"DBT_MODELS": "+gitlab+", "TARGET_BATCH_SIZE": "100"},
                ),
            ),
            (
                "with-empty-env",
                "{'tasks': ['tap target'], 'env': {}}",
                TaskSets(
                    name="with-empty-env",
                    tasks=["tap target"],
                    env={},
                ),
            ),
            # Test case for simple string format (backward compatibility)
            (
                "backward-compat-simple",
                "tap target",
                TaskSets(name="backward-compat-simple", tasks=["tap target"], env={}),
            ),
        ]

        for name, task_str, expected in cases:
            tset = tasks_from_yaml_str(name, task_str)
            assert tset.name == expected.name
            assert tset.tasks == expected.tasks
            # All TaskSets objects now have env field, compare directly
            assert tset.env == expected.env

        obvious_edge_cases = [
            ("bad-yaml", "['tap target'"),
            ("too-many-levels", "[[['tap target']]]"),
            ("non-string-list", "['tap target', 5"),
            # Invalid env var formats
            ("invalid-env-not-dict", "{'tasks': ['tap target'], 'env': 'not-a-dict'}"),
            ("invalid-env-values", "{'tasks': ['tap target'], 'env': {'KEY': 123}}"),
            ("missing-tasks-field", "{'env': {'KEY': 'value'}}"),
        ]

        for name, task_str in obvious_edge_cases:
            with pytest.raises(InvalidTasksError):
                tasks_from_yaml_str(name, task_str)
