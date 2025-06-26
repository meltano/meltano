from __future__ import annotations

import typing as t

from meltano.core._state import StateStrategy


class ELContextProtocol(t.Protocol):
    """Protocol for EL context classes."""

    state_strategy: StateStrategy

    def should_merge_states(self) -> bool:
        """Check whether the EL state is incomplete and should be merged."""
        return self.state_strategy == StateStrategy.MERGE
