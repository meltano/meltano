from __future__ import annotations

import logging
import typing as t
from pathlib import Path

import pytest
from click.testing import CliRunner

from fixtures.utils import cd, tmp_project
from meltano.core.project_files import ProjectFiles

if t.TYPE_CHECKING:
    from click import Command
    from click.testing import Result

    from fixtures.docker import SnowplowMicro


current_dir = Path(__file__).parent
plugins_dir = current_dir / "plugins"


class MeltanoCliRunner(CliRunner):
    def __init__(self, *args, snowplow: SnowplowMicro | None = None, **kwargs):
        """Initialize the `MeltanoCliRunner`."""
        self.snowplow = snowplow
        super().__init__(*args, **kwargs)

    def invoke(self, cli: Command, *args, **kwargs) -> Result:
        # `ctx.obj` is populated by the `cli` group callback, e.g. with the
        # `Tracker` used for this invocation. Passing our own dict lets us
        # inspect it after `invoke` returns, since it's mutated in place.
        obj = kwargs.setdefault("obj", {})
        results = super().invoke(cli, *args, **kwargs)
        # Outside of tests, telemetry events are flushed when the process
        # exits (see `meltano.cli.main`). Since `CliRunner.invoke` runs the
        # CLI in-process without going through `main`, that flush never
        # happens, so we replicate it here to ensure events reach the
        # Snowplow collector before the test asserts on them.
        tracker = obj.get("tracker")
        if tracker is not None and tracker.snowplow_tracker is not None:
            tracker.snowplow_tracker.flush()
        if self.snowplow:  # pragma: no cover
            assert self.snowplow.all()["bad"] == 0  # pragma: no cover
            assert not self.snowplow.bad()  # pragma: no cover
        return results


@pytest.fixture
def cli_runner(pushd, snowplow_optional: SnowplowMicro | None):
    pushd(Path.cwd())  # Ensure we return to the CWD after the test
    root_logger = logging.getLogger()  # noqa: TID251
    log_level = root_logger.level
    try:
        yield MeltanoCliRunner(snowplow=snowplow_optional)
    finally:
        root_logger.setLevel(log_level)


@pytest.fixture(scope="class")
def large_config_project(
    compatible_copy_tree,
    tmp_path_factory: pytest.TempPathFactory,
):
    with (
        cd(tmp_path_factory.mktemp("meltano-large-config-project")),
        tmp_project(
            "large_config_project",
            current_dir / "large_config_project",
            compatible_copy_tree,
        ) as project,
    ):
        yield project


@pytest.fixture(scope="class")
def project_files_cli(compatible_copy_tree, tmp_path_factory: pytest.TempPathFactory):
    with (
        cd(tmp_path_factory.mktemp("meltano-project-files-cli")),
        tmp_project(
            "a_multifile_meltano_project_cli",
            current_dir / "multifile_project",
            compatible_copy_tree,
        ) as project,
    ):
        yield ProjectFiles(root=project.root, meltano_file_path=project.meltanofile)
