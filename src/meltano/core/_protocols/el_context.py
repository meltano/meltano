from __future__ import annotations

import typing as t

from meltano.core._state import StateStrategy


class ELContextProtocol(t.Protocol):
    """Protocol for EL context classes."""

    full_refresh: bool | None
    select_filter: list[str]
    state_strategy: StateStrategy

    def should_merge_states(self) -> bool:
        """Check whether the EL state is incomplete and should be merged."""
        return (
            self.full_refresh is True and len(self.select_filter) > 0
        ) or self.state_strategy == StateStrategy.MERGE
