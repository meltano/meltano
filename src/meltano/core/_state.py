from __future__ import annotations

import enum
import sys

import structlog

if sys.version_info < (3, 11):
    from backports.strenum import StrEnum
else:
    from enum import StrEnum

logger = structlog.stdlib.get_logger()


class StateStrategy(StrEnum):
    """Strategy to use for state management."""

    AUTO = enum.auto()
    MERGE = enum.auto()
    OVERWRITE = enum.auto()

    @classmethod
    def from_cli_args(
        cls,
        *,
        merge_state: bool,
        state_strategy: str,
    ) -> StateStrategy:
        if merge_state and state_strategy != StateStrategy.AUTO.value:
            import click

            msg = "Cannot use both --merge-state and --state-strategy"
            raise click.UsageError(msg)

        if merge_state:
            logger.warning(
                "The --merge-state option is deprecated and will be removed in a "
                "future version. Use --state-strategy=merge instead.",
            )
            return StateStrategy.MERGE

        return StateStrategy(state_strategy)
