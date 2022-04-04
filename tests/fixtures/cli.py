import logging
import os
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from meltano.core.project import Project
from meltano.core.project_files import ProjectFiles
from meltano.core.project_init_service import ProjectInitService


@pytest.fixture()
def cli_runner(pushd):
    # this will make sure we are back at `cwd`
    # after this test is finished
    pushd(os.getcwd())

    yield CliRunner(mix_stderr=False)


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
