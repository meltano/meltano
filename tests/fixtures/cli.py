from __future__ import annotations

import logging
import typing as t
from pathlib import Path
from time import monotonic, sleep

import pytest
from click.testing import CliRunner

from fixtures.utils import cd, tmp_project
from meltano.core.project_files import ProjectFiles

if t.TYPE_CHECKING:
    from click import Command
    from click.testing import Result

    from fixtures.docker import SnowplowMicro
    from meltano.core.tracking.tracker import Tracker


current_dir = Path(__file__).parent
plugins_dir = current_dir / "plugins"


class MeltanoCliRunner(CliRunner):
    def __init__(self, *args, snowplow: SnowplowMicro | None = None, **kwargs):
        """Initialize the `MeltanoCliRunner`."""
        self.snowplow = snowplow
        super().__init__(*args, **kwargs)

    def invoke(self, cli: Command, *args, **kwargs) -> Result:
        obj = kwargs.setdefault("obj", {})
        results = super().invoke(cli, *args, **kwargs)
        if self.snowplow:  # pragma: no cover
            baseline = self.snowplow.all()
            # The tracker buffers events and only flushes them once enough
            # have accumulated, or when the process exits. Neither of those
            # is guaranteed to have happened by the time `invoke` returns, so
            # force a flush here to ensure events fired by this invocation
            # are sent to Snowplow Micro before we return.
            tracker: Tracker = obj.get("tracker")
            if tracker is not None and tracker.snowplow_tracker is not None:
                tracker.snowplow_tracker.flush()

                # Snowplow Micro returns HTTP 200 for a POST before it has
                # committed the event to its queryable store, so poll briefly
                # until the events sent above actually show up. Without this,
                # a subsequent test's `snowplow.reset()` (which runs in this
                # test's teardown) could race with Snowplow Micro still
                # processing these events, leaking them into a later test.
                deadline = monotonic() + 5.0
                expected = baseline["good"] + baseline["bad"] + 1
                summary = self.snowplow.all()
                while (
                    summary["good"] + summary["bad"] < expected
                    and monotonic() < deadline
                ):
                    sleep(0.1)
                    summary = self.snowplow.all()
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
