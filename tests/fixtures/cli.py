from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from click.testing import CliRunner

from meltano.core.project import Project
from meltano.core.project_files import ProjectFiles
from meltano.core.project_init_service import ProjectInitService

if TYPE_CHECKING:
    from fixtures.docker import SnowplowMicro


class MeltanoCliRunner(CliRunner):
    def __init__(self, *args, snowplow: SnowplowMicro | None = None, **kwargs):
        """Initialize the `MeltanoCliRunner`."""
        self.snowplow = snowplow
        super().__init__(*args, **kwargs)

    def invoke(self, *args, **kwargs) -> Any:
        results = super().invoke(*args, **kwargs)
        if self.snowplow:
            assert self.snowplow.all()["bad"] == 0
        return results


@pytest.fixture()
def cli_runner(pushd, snowplow_optional: SnowplowMicro | None):
    pushd(os.getcwd())  # Ensure the CWD is reset after the test
    return MeltanoCliRunner(mix_stderr=False, snowplow=snowplow_optional)


@pytest.fixture(scope="class")
def project_files_cli(test_dir, compatible_copy_tree):
    project_init_service = ProjectInitService("a_multifile_meltano_project_cli")
    project = project_init_service.init(add_discovery=False)
    logging.debug(f"Created new project at {project.root}")

    current_dir = Path(__file__).parent
    multifile_project_root = current_dir.joinpath("multifile_project/")

    os.remove(project.meltanofile)
    compatible_copy_tree(multifile_project_root, project.root)
    # cd into the new project root
    os.chdir(project.root)

    yield ProjectFiles(root=project.root, meltano_file_path=project.meltanofile)

    # clean-up
    Project.deactivate()
    os.chdir(test_dir)
    shutil.rmtree(project.root)
    logging.debug(f"Cleaned project at {project.root}")
