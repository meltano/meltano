from __future__ import annotations

import asyncio

import pytest

from meltano.core.logging.utils import capture_subprocess_output


class AsyncReader(asyncio.StreamReader):
    def __init__(self, lines: list[bytes]):
        self.lines = lines

    def at_eof(self) -> bool:
        return not self.lines

    async def readline(self) -> bytes:
        return self.lines.pop(0) if self.lines else b""


@pytest.mark.asyncio()
async def test_capture_subprocess_output() -> None:
    input_lines = [b"LINE\n", b"LINE 2\n", b"\xed\n"]
    output_lines = []

    class LineWriter:
        def writeline(self, line: str) -> None:
            output_lines.append(line)

    reader = AsyncReader(input_lines)

    await capture_subprocess_output(reader, LineWriter())
    assert output_lines == ["LINE\n", "LINE 2\n", "�\n"]
