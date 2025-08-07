from __future__ import annotations

from meltano.core.block.block_parser import is_command_block


class TestParserUtils:
    def test_is_command_block(self, tap, dbt) -> None:
        assert not is_command_block(tap)
        assert is_command_block(dbt)
