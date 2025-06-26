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
        state_strategy: StateStrategy,
    ):
        self.full_refresh = full_refresh
        self.state_strategy = state_strategy


class TestELContextProtocol:
    def test_should_merge_states(self, subtests: SubTests):
        with subtests.test("Full refresh & auto → merge"):
            assert MyContext(
                full_refresh=True,
                state_strategy=StateStrategy.AUTO,
            ).should_merge_states()

        with subtests.test("Full refresh & merge → merge"):
            assert MyContext(
                full_refresh=True,
                state_strategy=StateStrategy.MERGE,
            ).should_merge_states()

        with subtests.test("Full refresh & overwrite → overwrite"):
            assert not MyContext(
                full_refresh=True,
                state_strategy=StateStrategy.OVERWRITE,
            ).should_merge_states()

        with subtests.test("Incremental & auto → overwrite"):
            assert not MyContext(
                full_refresh=False,
                state_strategy=StateStrategy.AUTO,
            ).should_merge_states()

        with subtests.test("Incremental & merge → merge"):
            assert MyContext(
                full_refresh=False,
                state_strategy=StateStrategy.MERGE,
            ).should_merge_states()

        with subtests.test("Incremental & overwrite → overwrite"):
            assert not MyContext(
                full_refresh=False,
                state_strategy=StateStrategy.OVERWRITE,
            ).should_merge_states()
