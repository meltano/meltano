from __future__ import annotations

from meltano.core.block.parser import is_command_block


class TestParserUtils:
    def test_is_command_block(self, tap, dbt):
        """Verify that the is_command_block function returns True when the block is an IOBlock and has a command."""
        assert not is_command_block(tap)
        assert is_command_block(dbt)
