from __future__ import annotations

import typing as t
from time import monotonic, sleep

import pytest

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.utils import hash_sha256

if t.TYPE_CHECKING:
    from fixtures.cli import MeltanoCliRunner
    from fixtures.docker import SnowplowMicro


def _flush_tracker(obj: dict) -> None:
    """Flush the `Tracker` used for a CLI invocation, if any.

    Outside of tests, telemetry events are flushed when the process exits
    (see `meltano.cli.main`). Since `CliRunner.invoke` runs the CLI
    in-process without going through `main`, that flush never happens, so
    it's replicated here to ensure events reach the Snowplow collector
    before this test asserts on them.
    """
    tracker = obj.get("tracker")
    if tracker is not None and tracker.snowplow_tracker is not None:
        tracker.snowplow_tracker.flush()


def _good_events(snowplow: SnowplowMicro, *, timeout: float = 10.0) -> list[dict]:
    """Poll Snowplow Micro for good events, allowing for its async processing.

    Snowplow Micro returns HTTP 200 for a submitted event before it has
    finished validating and storing it, so querying `good()` immediately
    after sending events is prone to a race condition.
    """
    deadline = monotonic() + timeout
    events = snowplow.good()
    while not events and monotonic() < deadline:  # pragma: no cover
        sleep(0.1)
        events = snowplow.good()
    return events


@pytest.mark.parametrize(
    ("cmd", "expected"),
    (
        ("test", hash_sha256("dev")),
        ("--no-environment test", None),
        ("schedule list", None),
        ("--environment=dev schedule list", hash_sha256("dev")),
        ("--environment=prod schedule list", hash_sha256("prod")),
    ),
    ids=(
        "default-dev",
        "explicit-no-env",
        "default-no-env",
        "explicit-dev",
        "explicit-prod",
    ),
)
@pytest.mark.usefixtures("project")
def test_environment_name_hash(
    cmd: str,
    expected: str,
    snowplow: SnowplowMicro,
    cli_runner: MeltanoCliRunner,
) -> None:
    # `ctx.obj` is populated by the `cli` group callback, e.g. with the
    # `Tracker` used for this invocation. Passing our own dict lets us
    # inspect it after `invoke` returns, since it's mutated in place.
    obj: dict = {}
    results = cli_runner.invoke(cli, cmd.split(), obj=obj)
    assert_cli_runner(results)
    _flush_tracker(obj)
    good_events = _good_events(snowplow)
    assert good_events
    for event in good_events:
        project_context = next(
            ctx
            for ctx in event["event"]["contexts"]["data"]
            if "project_context" in ctx["schema"]
        )
        assert project_context["data"]["environment_name_hash"] == expected
