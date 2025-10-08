from __future__ import annotations

import typing as t

from meltano.core._state import StateStrategy


class ELContextProtocol(t.Protocol):
    """Protocol for EL context classes."""

    full_refresh: bool | None
    state_strategy: StateStrategy
    refresh_catalog: bool | None

    def should_merge_states(self) -> bool:
        """Check whether the EL state is incomplete and should be merged."""
        return (
            self.full_refresh is True  # Full refresh implies merging states
            and self.state_strategy == StateStrategy.auto
        ) or self.state_strategy == StateStrategy.merge

    def should_refresh_catalog(self) -> bool:
        """Check whether the catalog should be refreshed or used from cache."""
        return self.refresh_catalog is True or self.full_refresh is True
