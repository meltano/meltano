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
async def test_capture_subprocess_output():
    INPUT_LINES = [b"LINE\n", b"LINE 2\n", b"\xed\n"]
    OUTPUT_LINES = []

    class LineWriter:
        def writeline(self, line: str):
            OUTPUT_LINES.append(line)

    reader = AsyncReader(INPUT_LINES)

    await capture_subprocess_output(reader, LineWriter())
    assert ["LINE\n", "LINE 2\n", "�\n"] == OUTPUT_LINES
