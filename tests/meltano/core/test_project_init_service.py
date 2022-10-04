from __future__ import annotations

import platform
import shutil
import stat
from typing import TYPE_CHECKING

import pytest

from meltano.core.project_init_service import (
    ProjectInitService,
    ProjectInitServiceError,
)

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize(
    "create_project_dir",
    (
        False,
        True,
    ),
    ids=(
        "new directory",
        "empty directory",
    ),
)
def test_project_init_success(create_project_dir: bool, tmp_path: Path, pushd):
    project_name = "test_project"

    projects_dir = tmp_path.joinpath("success")
    projects_dir.mkdir()
    pushd(projects_dir)

    project_dir = projects_dir.joinpath(project_name)

    if create_project_dir:
        project_dir.mkdir()

    ProjectInitService(project_name).init(activate=False, add_discovery=False)

    shutil.rmtree(project_dir)

    if create_project_dir:
        project_dir.mkdir()

    ProjectInitService(f"{project_dir.absolute()}").init(
        activate=False, add_discovery=False
    )


def test_project_init_non_empty_directory(tmp_path: Path, pushd):
    project_name = "test_project"

    projects_dir = tmp_path.joinpath("exists")
    projects_dir.joinpath(project_name, "test").mkdir(parents=True)
    pushd(projects_dir)
    with pytest.raises(
        ProjectInitServiceError,
        match=f"Directory {project_name!r} not empty",
    ):
        ProjectInitService(project_name).init(activate=False, add_discovery=False)


def test_project_init_no_write_permission(tmp_path: Path, pushd):
    if platform.system() == "Windows":
        pytest.xfail(
            "Windows can still create new directories inside a read-only directory."
        )
    project_name = "test_project"

    protected_dir = tmp_path.joinpath("protected")
    protected_dir.mkdir()
    protected_dir.chmod(stat.S_IREAD | stat.S_IEXEC)  # read and execute, but not write
    pushd(protected_dir)
    with pytest.raises(
        ProjectInitServiceError,
        match=f"Permission denied to create {project_name!r}",
    ):
        ProjectInitService(project_name).init(activate=False, add_discovery=False)


def test_project_init_missing_parent_directory(tmp_path: Path, pushd):
    if platform.system() == "Windows":
        pytest.xfail(
            "Windows can't remove a directory that is in use. See https://docs.python.org/3/library/os.html#os.remove"
        )
    project_name = "test_project"

    missing_dir = tmp_path.joinpath("missing")
    missing_dir.mkdir()
    pushd(missing_dir)
    missing_dir.rmdir()  # remove the parent directory
    with pytest.raises(
        ProjectInitServiceError,
        match=f"Could not create directory {project_name!r}.",
    ):
        ProjectInitService(project_name).init(activate=False, add_discovery=False)
