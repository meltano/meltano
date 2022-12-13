from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.utils import hash_sha256

if TYPE_CHECKING:
    from fixtures.cli import MeltanoCliRunner
    from fixtures.docker import SnowplowMicro
    from meltano.core.project import Project


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
def test_environment_name_hash(
    cmd: str,
    expected: str,
    snowplow: SnowplowMicro,
    cli_runner: MeltanoCliRunner,
    project: Project,
):
    results = cli_runner.invoke(cli, cmd.split())
    assert_cli_runner(results)
    for event in snowplow.good():
        project_context = next(
            ctx
            for ctx in event["event"]["contexts"]["data"]
            if "project_context" in ctx["schema"]
        )
        assert project_context["data"]["environment_name_hash"] == expected
