from __future__ import annotations

from meltano.core._protocols.el_context import ELContextProtocol
from meltano.core._state import StateStrategy


class MyContext(ELContextProtocol):
    def __init__(
        self,
        *,
        state_strategy: StateStrategy,
    ):
        self.state_strategy = state_strategy


class TestELContextProtocol:
    def test_should_merge_states(self):
        assert MyContext(state_strategy=StateStrategy.MERGE).should_merge_states()
        assert not MyContext(
            state_strategy=StateStrategy.OVERWRITE
        ).should_merge_states()
