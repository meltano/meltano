"""Benchmarks for SingerTap catalog operations.

These benchmarks measure the performance of catalog discovery and rule
application, which were affected by the async I/O changes in commit f3fa5b450.

This exercises the anyio.open_file() read/write paths with real disk I/O,
complementing the isolated _stream_redirect benchmarks.
"""

from __future__ import annotations

import asyncio
import json
import typing as t
from unittest import mock
from unittest.mock import AsyncMock

import pytest

from meltano.core.plugin_invoker import PluginInvoker

if t.TYPE_CHECKING:
    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.plugin.singer import SingerTap
    from meltano.core.project_add_service import ProjectAddService


def generate_catalog(num_streams: int = 10, properties_per_stream: int = 30) -> dict:
    """Generate a realistic Singer catalog for benchmarking."""
    streams = []
    for i in range(num_streams):
        properties = {
            f"property_{j}": {"type": ["null", "string"]}
            for j in range(properties_per_stream)
        }
        streams.append(
            {
                "tap_stream_id": f"stream_{i}",
                "stream": f"stream_{i}",
                "schema": {"type": "object", "properties": properties},
                "metadata": [{"breadcrumb": [], "metadata": {"selected": True}}],
            }
        )
    return {"streams": streams}


class MockStdout:
    """Mock stdout that yields catalog data line by line.

    This class avoids closure/iterator issues by using an index-based approach.
    """

    def __init__(self, lines: list[bytes]) -> None:
        self.lines = lines
        self.index = 0

    def reset(self) -> None:
        """Reset to beginning for reuse."""
        self.index = 0

    def at_eof(self) -> bool:
        return self.index >= len(self.lines)

    async def readline(self) -> bytes:
        if self.index >= len(self.lines):
            return b""
        line = self.lines[self.index]
        self.index += 1
        return line


class MockStderr:
    """Mock stderr that returns EOF immediately."""

    def at_eof(self) -> bool:
        return True

    async def readline(self) -> bytes:
        return b""


class TestTapBenchmarks:
    """Benchmarks for SingerTap catalog operations."""

    @pytest.fixture(scope="class")
    def tap_plugin(self, project_add_service: ProjectAddService) -> SingerTap:
        """Create tap plugin once per test class."""
        from meltano.core.plugin import PluginType

        return project_add_service.add(PluginType.EXTRACTORS, "tap-mock")

    @pytest.fixture(scope="class")
    def catalog(self) -> dict:
        """Pre-generate catalog once per test class."""
        return generate_catalog()

    @pytest.fixture(scope="class")
    def catalog_lines(self, catalog: dict) -> list[bytes]:
        """Pre-compute catalog lines once per test class."""
        catalog_json = json.dumps(catalog, indent=2)
        return [line.encode() + b"\n" for line in catalog_json.split("\n")]

    @pytest.mark.benchmark
    def test_discover_catalog(
        self,
        session,
        tap_plugin: SingerTap,
        catalog_lines: list[bytes],
        plugin_invoker_factory: t.Callable[[ProjectPlugin], PluginInvoker],
        benchmark,
    ) -> None:
        """Benchmark catalog discovery with mocked subprocess.

        This exercises the _stream_redirect function writing to a real file,
        which uses anyio.open_file() in async mode.
        """
        invoker = plugin_invoker_factory(tap_plugin)

        # Create mock objects once, reuse across the benchmark
        mock_stdout = MockStdout(catalog_lines)
        mock_stderr = MockStderr()

        process_mock = mock.Mock()
        process_mock.stdout = mock_stdout
        process_mock.stderr = mock_stderr
        process_mock.wait = AsyncMock(return_value=0)
        process_mock.returncode = 0

        async def run_discovery() -> None:
            async with invoker.prepared(session):
                mock_stdout.reset()
                invoker.invoke_async = AsyncMock(return_value=process_mock)

                with mock.patch.object(
                    PluginInvoker,
                    "stderr_logger",
                    new_callable=mock.PropertyMock,
                    return_value=mock.Mock(isEnabledFor=mock.Mock(return_value=False)),
                ):
                    await tap_plugin.discover_catalog(invoker)

        # Use pedantic mode with warmup for more stable async benchmarks
        benchmark.pedantic(
            lambda: asyncio.run(run_discovery()),
            rounds=10,
            warmup_rounds=5,
        )

    @pytest.mark.benchmark
    def test_apply_catalog_rules(
        self,
        session,
        tap_plugin: SingerTap,
        catalog: dict,
        plugin_invoker_factory: t.Callable[[ProjectPlugin], PluginInvoker],
        benchmark,
    ) -> None:
        """Benchmark applying catalog rules with real file I/O.

        This exercises the anyio.open_file() read/write paths that were
        changed in commit f3fa5b450.
        """
        invoker = plugin_invoker_factory(tap_plugin)
        catalog_json = json.dumps(catalog)

        async def apply_rules() -> None:
            async with invoker.prepared(session):
                invoker.files["catalog"].write_text(catalog_json)
                await tap_plugin.apply_catalog_rules(invoker)

        # Use pedantic mode with warmup for more stable async benchmarks
        benchmark.pedantic(
            lambda: asyncio.run(apply_rules()),
            rounds=10,
            warmup_rounds=5,
        )
