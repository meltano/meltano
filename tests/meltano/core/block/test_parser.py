from __future__ import annotations  # noqa: INP001

from meltano.core.block.parser import is_command_block


class TestParserUtils:
    def test_is_command_block(self, tap, dbt):  # noqa: ANN001, ANN201
        assert not is_command_block(tap)
        assert is_command_block(dbt)
