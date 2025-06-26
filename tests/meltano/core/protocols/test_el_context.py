# ruff: noqa: FBT001, FBT003

from __future__ import annotations

import typing as t
from dataclasses import dataclass

from meltano.core._protocols.el_context import ELContextProtocol
from meltano.core._state import StateStrategy

if t.TYPE_CHECKING:
    from pytest_subtests import SubTests


@dataclass
class MyContext(ELContextProtocol):
    full_refresh: bool | None
    state_strategy: StateStrategy


class TestELContextProtocol:
    def test_should_merge_states(self, subtests: SubTests):
        def _(full_refresh: bool, state_strategy: StateStrategy):
            return MyContext(full_refresh, state_strategy)

        with subtests.test("Full refresh & auto → merge"):
            assert _(True, StateStrategy.AUTO).should_merge_states()

        with subtests.test("Full refresh & merge → merge"):
            assert _(True, StateStrategy.MERGE).should_merge_states()

        with subtests.test("Full refresh & overwrite → overwrite"):
            assert not _(True, StateStrategy.OVERWRITE).should_merge_states()

        with subtests.test("Incremental & auto → overwrite"):
            assert not _(False, StateStrategy.AUTO).should_merge_states()

        with subtests.test("Incremental & merge → merge"):
            assert _(False, StateStrategy.MERGE).should_merge_states()

        with subtests.test("Incremental & overwrite → overwrite"):
            assert not _(False, StateStrategy.OVERWRITE).should_merge_states()
