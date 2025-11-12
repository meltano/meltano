# ruff: noqa: FBT001, FBT003

from __future__ import annotations

import typing as t
from dataclasses import dataclass

from meltano.core._protocols.el_context import ELContextProtocol
from meltano.core._state import StateStrategy

if t.TYPE_CHECKING:
    import pytest


@dataclass
class MyContext(ELContextProtocol):
    full_refresh: bool | None = None
    state_strategy: StateStrategy = StateStrategy.auto
    refresh_catalog: bool | None = None


class TestELContextProtocol:
    def test_should_merge_states(self, subtests: pytest.Subtests):
        def _(full_refresh: bool, state_strategy: StateStrategy):
            return MyContext(full_refresh, state_strategy)

        with subtests.test("Full refresh & auto → merge"):
            assert _(True, StateStrategy.auto).should_merge_states()

        with subtests.test("Full refresh & merge → merge"):
            assert _(True, StateStrategy.merge).should_merge_states()

        with subtests.test("Full refresh & overwrite → overwrite"):
            assert not _(True, StateStrategy.overwrite).should_merge_states()

        with subtests.test("Incremental & auto → overwrite"):
            assert not _(False, StateStrategy.auto).should_merge_states()

        with subtests.test("Incremental & merge → merge"):
            assert _(False, StateStrategy.merge).should_merge_states()

        with subtests.test("Incremental & overwrite → overwrite"):
            assert not _(False, StateStrategy.overwrite).should_merge_states()

    def test_should_refresh_catalog(self, subtests: pytest.Subtests):
        def _(full_refresh: bool, refresh_catalog: bool):
            return MyContext(full_refresh, refresh_catalog=refresh_catalog)

        with subtests.test("Refresh catalog & full refresh → refresh catalog"):
            assert _(True, True).should_refresh_catalog()

        with subtests.test("Refresh catalog & incremental → refresh catalog"):
            assert _(False, True).should_refresh_catalog()
            assert _(None, True).should_refresh_catalog()

        with subtests.test("No refresh catalog & full refresh → refresh catalog"):
            assert _(True, False).should_refresh_catalog()
            assert _(True, None).should_refresh_catalog()

        with subtests.test("No refresh catalog & incremental → use cached catalog"):
            assert not _(False, False).should_refresh_catalog()
            assert not _(False, None).should_refresh_catalog()
            assert not _(None, None).should_refresh_catalog()
