from __future__ import annotations

import typing as t
from time import monotonic, sleep

import pytest

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.tracking.contexts import ProjectContext
from meltano.core.utils import hash_sha256

if t.TYPE_CHECKING:
    from fixtures.cli import MeltanoCliRunner
    from fixtures.docker import SnowplowMicro
    from meltano.core.tracking import Tracker


def _flush_tracker(obj: dict) -> str | None:  # pragma: no cover
    """Flush the `Tracker` used for a CLI invocation, if any.

    Outside of tests, telemetry events are flushed when the process exits
    (see `meltano.cli.main`). Since `CliRunner.invoke` runs the CLI
    in-process without going through `main`, that flush never happens, so
    it's replicated here to ensure events reach the Snowplow collector
    before this test asserts on them.

    Returns:
        The `context_uuid` of this invocation's `ProjectContext`, if any,
        so that events from this invocation can be told apart from those
        of other invocations once they reach Snowplow Micro.
    """
    tracker: Tracker | None = obj.get("tracker")
    if tracker is None:
        return None

    if tracker.snowplow_tracker is not None:
        tracker.snowplow_tracker.flush()

    return next(
        ctx.data["context_uuid"]
        for ctx in tracker.contexts
        if isinstance(ctx, ProjectContext)
    )


def _project_context(event: dict) -> dict:
    return next(
        ctx
        for ctx in event["event"]["contexts"]["data"]
        if "project_context" in ctx["schema"]
    )


def _good_events(
    snowplow: SnowplowMicro,
    *,
    context_uuid: str | None,
    timeout: float = 10.0,
) -> list[dict]:
    """Poll Snowplow Micro for events fired by this invocation.

    Snowplow Micro returns HTTP 200 for a submitted event before it has
    finished validating and storing it, so querying `good()` immediately
    after sending events is prone to a race condition. Additionally, since
    `snowplow.reset()` (used between tests) doesn't wait for events still
    in flight, a previous test's events can show up here after this test
    has already sent its own. Filtering by `context_uuid` -- unique to
    each invocation's `ProjectContext` -- keeps the two from being confused.
    """

    def matching_events() -> list[dict]:
        return [
            event
            for event in snowplow.good()
            if _project_context(event)["data"]["context_uuid"] == context_uuid
        ]

    deadline = monotonic() + timeout
    events = matching_events()
    while not events and monotonic() < deadline:  # pragma: no cover
        sleep(0.1)
        events = matching_events()
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
    context_uuid = _flush_tracker(obj)
    good_events = _good_events(snowplow, context_uuid=context_uuid)
    assert good_events
    for event in good_events:
        project_context = _project_context(event)
        assert project_context["data"]["environment_name_hash"] == expected
