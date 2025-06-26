from __future__ import annotations

import typing as t

from meltano.core._protocols.el_context import ELContextProtocol
from meltano.core._state import StateStrategy

if t.TYPE_CHECKING:
    from pytest_subtests import SubTests


class MyContext(ELContextProtocol):
    def __init__(
        self,
        *,
        full_refresh: bool | None,
        select_filter: list[str],
        state_strategy: StateStrategy,
    ):
        self.full_refresh = full_refresh
        self.select_filter = select_filter
        self.state_strategy = state_strategy


class TestELContextProtocol:
    def test_incomplete_state(self, subtests: SubTests):
        with subtests.test("Full refresh + stream selection = merge"):
            assert MyContext(
                full_refresh=True,
                select_filter=["a", "b"],
                state_strategy=StateStrategy.MERGE,
            ).should_merge_states()

            assert MyContext(
                full_refresh=True,
                select_filter=["a", "b"],
                state_strategy=StateStrategy.OVERWRITE,
            ).should_merge_states()

        with subtests.test("No stream selection + merge strategy = merge"):
            assert MyContext(
                full_refresh=True,
                select_filter=[],
                state_strategy=StateStrategy.MERGE,
            ).should_merge_states()

        with subtests.test("No stream selection + overwrite strategy = overwrite"):
            assert not MyContext(
                full_refresh=True,
                select_filter=[],
                state_strategy=StateStrategy.OVERWRITE,
            ).should_merge_states()

        with subtests.test("Incremental + merge strategy = merge"):
            assert MyContext(
                full_refresh=False,
                select_filter=["a", "b"],
                state_strategy=StateStrategy.MERGE,
            ).should_merge_states()

        with subtests.test("Incremental + overwrite strategy = overwrite"):
            assert not MyContext(
                full_refresh=False,
                select_filter=["a", "b"],
                state_strategy=StateStrategy.OVERWRITE,
            ).should_merge_states()
