from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from click import Command
from click.testing import CliRunner

from fixtures.utils import tmp_project
from meltano.core.project_files import ProjectFiles

if TYPE_CHECKING:
    from click.testing import Result

    from fixtures.docker import SnowplowMicro


current_dir = Path(__file__).parent


class MeltanoCliRunner(CliRunner):
    def __init__(self, *args, snowplow: SnowplowMicro | None = None, **kwargs):
        """Initialize the `MeltanoCliRunner`."""
        self.snowplow = snowplow
        super().__init__(*args, **kwargs)

    def invoke(self, cli: Command, *args, **kwargs) -> Result:
        results = super().invoke(cli, *args, **kwargs)
        if self.snowplow:  # pragma: no cover
            assert self.snowplow.all()["bad"] == 0  # pragma: no cover
            assert not self.snowplow.bad()  # pragma: no cover
        return results


@pytest.fixture
def cli_runner(pushd, snowplow_optional: SnowplowMicro | None):
    pushd(os.getcwd())  # Ensure we return to the CWD after the test
    root_logger = logging.getLogger()
    log_level = root_logger.level
    try:
        yield MeltanoCliRunner(mix_stderr=False, snowplow=snowplow_optional)
    finally:
        root_logger.setLevel(log_level)


@pytest.fixture(scope="class")
def large_config_project(test_dir, compatible_copy_tree):
    with tmp_project(
        "large_config_project",
        current_dir / "large_config_project",
        compatible_copy_tree,
    ) as project:
        yield project


@pytest.fixture(scope="class")
def project_files_cli(test_dir, compatible_copy_tree):
    with tmp_project(
        "a_multifile_meltano_project_cli",
        current_dir / "multifile_project",
        compatible_copy_tree,
    ) as project:
        yield ProjectFiles(root=project.root, meltano_file_path=project.meltanofile)
