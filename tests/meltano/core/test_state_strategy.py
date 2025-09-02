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
                state_strategy=StateStrategy.auto.value,
            )
            is StateStrategy.merge
        )

        assert (
            StateStrategy.from_cli_args(
                merge_state=False,
                state_strategy=StateStrategy.auto.value,
            )
            is StateStrategy.auto
        )

        assert (
            StateStrategy.from_cli_args(
                merge_state=False,
                state_strategy=StateStrategy.merge,
            )
            is StateStrategy.merge
        )

        assert (
            StateStrategy.from_cli_args(
                merge_state=False,
                state_strategy=StateStrategy.overwrite,
            )
            is StateStrategy.overwrite
        )

        with pytest.raises(click.UsageError):
            StateStrategy.from_cli_args(
                merge_state=True,
                state_strategy=StateStrategy.merge,
            )

        with pytest.raises(click.UsageError):
            StateStrategy.from_cli_args(
                merge_state=True,
                state_strategy=StateStrategy.overwrite,
            )
