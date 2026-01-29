from __future__ import annotations

import json
import typing as t
from unittest import mock
from unittest.mock import AsyncMock

import pytest

from meltano.core.plugin import PluginType
from meltano.core.plugin_invoker import PluginInvoker

if t.TYPE_CHECKING:
    from collections.abc import Callable

    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.plugin.singer import SingerTap
    from meltano.core.project_add_service import ProjectAddService


def generate_catalog(num_streams: int = 50, properties_per_stream: int = 100) -> dict:
    """Generate a realistic Singer catalog for benchmarking.

    Args:
        num_streams: Number of streams in the catalog.
        properties_per_stream: Number of properties per stream.

    Returns:
        A Singer catalog dictionary.
    """
    streams = []
    for i in range(num_streams):
        properties = {}
        for j in range(properties_per_stream):
            properties[f"property_{j}"] = {
                "type": ["null", "string"],
                "description": f"Description for property {j} in stream {i}",
            }

        streams.append(
            {
                "tap_stream_id": f"stream_{i}",
                "stream": f"stream_{i}",
                "schema": {
                    "type": "object",
                    "properties": properties,
                },
                "metadata": [
                    {
                        "breadcrumb": [],
                        "metadata": {
                            "selected": True,
                            "replication-method": "INCREMENTAL",
                            "replication-key": "updated_at",
                        },
                    },
                    *[
                        {
                            "breadcrumb": ["properties", f"property_{j}"],
                            "metadata": {"selected": True},
                        }
                        for j in range(properties_per_stream)
                    ],
                ],
            }
        )

    return {"streams": streams}


def create_mock_process(catalog_json: str) -> mock.Mock:
    """Create a mock subprocess that simulates tap --discover output.

    The mock process yields the catalog JSON line by line through stdout,
    which exercises the _stream_redirect function's async file I/O.

    Args:
        catalog_json: The JSON string to output through stdout.

    Returns:
        A mock process object.
    """
    # Split catalog into lines to simulate realistic subprocess output
    # Singer taps typically output the full JSON, but we split by lines
    # to exercise _stream_redirect's line-by-line reading
    lines = catalog_json.encode("utf-8").split(b"\n")
    line_iter = iter(lines)

    def readline_side_effect() -> bytes:
        try:
            return next(line_iter) + b"\n"
        except StopIteration:
            return b""

    # Track EOF state based on whether we've exhausted lines
    eof_called = {"count": 0, "total_lines": len(lines)}

    def at_eof_side_effect() -> bool:
        eof_called["count"] += 1
        # Return False until we've read all lines, then True
        return eof_called["count"] > eof_called["total_lines"]

    process_mock = mock.Mock()
    process_mock.wait = AsyncMock(return_value=0)
    process_mock.returncode = 0

    # Mock stdout to yield catalog data line by line
    process_mock.stdout.at_eof.side_effect = at_eof_side_effect
    process_mock.stdout.readline = AsyncMock(side_effect=readline_side_effect)

    # Mock stderr to return EOF immediately (no stderr output)
    process_mock.stderr.at_eof.return_value = True
    process_mock.stderr.readline = AsyncMock(return_value=b"")

    return process_mock


class TestTapBenchmarks:
    """Benchmarks for SingerTap operations.

    These benchmarks help prevent performance regressions like the one
    identified in https://github.com/meltano/meltano/pull/9724, where
    switching to async I/O for catalog file operations caused slowdowns.
    """

    @pytest.fixture(scope="class")
    def subject(self, project_add_service: ProjectAddService) -> SingerTap:
        return project_add_service.add(PluginType.EXTRACTORS, "tap-mock")

    @pytest.fixture
    def large_catalog(self) -> dict:
        """Generate a catalog for benchmarking.

        Uses 10 streams x 30 properties = 300 total properties.
        With pretty-printed JSON, this creates ~5k lines - enough to
        detect regressions while keeping CI runtime reasonable.
        """
        return generate_catalog(num_streams=10, properties_per_stream=30)

    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_discover_catalog(
        self,
        session,
        plugin_invoker_factory: Callable[[ProjectPlugin], PluginInvoker],
        subject: SingerTap,
        large_catalog: dict,
    ) -> None:
        """Benchmark SingerTap.discover_catalog performance.

        This benchmark measures the time to:
        1. Run discovery via _stream_redirect (mocked subprocess stdout)
        2. Write catalog data through async file I/O
        3. Validate the catalog JSON

        The _stream_redirect async file I/O was the source of the regression
        in PR #9724, where async I/O was slower than sync I/O.
        """
        invoker = plugin_invoker_factory(subject)

        # Pretty-print JSON to create more lines for _stream_redirect to process
        catalog_json = json.dumps(large_catalog, indent=2)
        process_mock = create_mock_process(catalog_json)

        async with invoker.prepared(session):
            invoker.invoke_async = AsyncMock(return_value=process_mock)
            # Mock stderr_logger to avoid structlog compatibility issues
            with mock.patch.object(
                PluginInvoker,
                "stderr_logger",
                new_callable=mock.PropertyMock,
                return_value=mock.Mock(isEnabledFor=mock.Mock(return_value=False)),
            ):
                await subject.discover_catalog(invoker)

    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_apply_catalog_rules(
        self,
        session,
        plugin_invoker_factory: Callable[[ProjectPlugin], PluginInvoker],
        subject: SingerTap,
        large_catalog: dict,
    ) -> None:
        """Benchmark SingerTap.apply_catalog_rules performance.

        This benchmark measures the time to:
        1. Read the catalog file
        2. Apply metadata and schema rules
        3. Write the modified catalog back

        The file I/O and JSON parsing/serialization here was also affected
        by the regression in PR #9724.
        """
        invoker = plugin_invoker_factory(subject)
        catalog_path = invoker.files["catalog"]
        catalog_json = json.dumps(large_catalog)

        async with invoker.prepared(session):
            # Write the catalog file for apply_catalog_rules to process
            catalog_path.write_text(catalog_json)
            await subject.apply_catalog_rules(invoker)
