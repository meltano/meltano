from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

from meltano.core.project_init_service import (
    ProjectInitService,
    ProjectInitServiceError,
)

if TYPE_CHECKING:
    from pathlib import Path


def test_project_init_directory_exists(tmp_path: Path):
    project_name = "test_project"

    projects_dir = tmp_path.joinpath("exists")
    projects_dir.joinpath(project_name).mkdir(parents=True)
    os.chdir(projects_dir)
    with pytest.raises(
        ProjectInitServiceError,
        match="Directory test_project already exists",
    ):
        ProjectInitService(project_name).init(activate=False, add_discovery=False)


def test_project_init_no_write_permission(tmp_path: Path):
    project_name = "test_project"

    protected_dir = tmp_path.joinpath("protected")
    protected_dir.mkdir(mode=0o555)  # read and execute, but not write
    os.chdir(protected_dir)
    with pytest.raises(
        ProjectInitServiceError,
        match="Permission denied to create test_project",
    ):
        ProjectInitService(project_name).init(activate=False, add_discovery=False)


def test_project_init_missing_parent_directory(tmp_path: Path):
    project_name = "test_project"

    missing_dir = tmp_path.joinpath("missing")
    missing_dir.mkdir()
    os.chdir(missing_dir)
    missing_dir.rmdir()  # remove the parent directory
    with pytest.raises(
        ProjectInitServiceError,
        match="Could not create directory test_project.",
    ):
        ProjectInitService(project_name).init(activate=False, add_discovery=False)
