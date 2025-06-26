from __future__ import annotations

import click
import pytest

from meltano.core._state import StateStrategy


class TestStateStrategy:
    # TODO: Remove this test once we remove the `--merge-state` CLI flag
    def test_state_strategy_from_cli_args(self):
        assert (
            StateStrategy.from_cli_args(
                merge_state=True,
                state_strategy=StateStrategy.AUTO.value,
            )
            is StateStrategy.MERGE
        )

        assert (
            StateStrategy.from_cli_args(
                merge_state=False,
                state_strategy=StateStrategy.AUTO.value,
            )
            is StateStrategy.AUTO
        )

        assert (
            StateStrategy.from_cli_args(
                merge_state=False,
                state_strategy=StateStrategy.MERGE,
            )
            is StateStrategy.MERGE
        )

        assert (
            StateStrategy.from_cli_args(
                merge_state=False,
                state_strategy=StateStrategy.OVERWRITE,
            )
            is StateStrategy.OVERWRITE
        )

        with pytest.raises(click.UsageError):
            StateStrategy.from_cli_args(
                merge_state=True,
                state_strategy=StateStrategy.MERGE,
            )

        with pytest.raises(click.UsageError):
            StateStrategy.from_cli_args(
                merge_state=True,
                state_strategy=StateStrategy.OVERWRITE,
            )
