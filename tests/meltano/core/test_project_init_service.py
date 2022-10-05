from __future__ import annotations

import platform
import re
import shutil
import stat
from pathlib import Path

import pytest

from meltano.core.project_init_service import (
    ProjectInitService,
    ProjectInitServiceError,
)


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
    projects_dir = tmp_path.joinpath("success")
    projects_dir.mkdir()
    pushd(projects_dir)

    project_dir = projects_dir.joinpath("test_project")

    if create_project_dir:
        project_dir.mkdir()

    ProjectInitService(project_dir.relative_to(Path.cwd())).init(
        activate=False, add_discovery=False
    )

    shutil.rmtree(project_dir)

    if create_project_dir:
        project_dir.mkdir()

    ProjectInitService(project_dir.absolute()).init(activate=False, add_discovery=False)


def test_project_init_non_empty_directory(tmp_path: Path, pushd):
    projects_dir = tmp_path.joinpath("exists")
    projects_dir.mkdir()
    pushd(projects_dir)

    project_dir = projects_dir.joinpath("test_project")
    project_dir.joinpath("test").mkdir(parents=True)

    with pytest.raises(
        ProjectInitServiceError,
        match=re.escape(f"Directory '{project_dir}' not empty"),
    ):
        ProjectInitService(project_dir).init(activate=False, add_discovery=False)


def test_project_init_no_write_permission(tmp_path: Path, pushd):
    if platform.system() == "Windows":
        pytest.xfail(
            "Windows can still create new directories inside a read-only directory."
        )

    protected_dir = tmp_path.joinpath("protected")
    protected_dir.mkdir()
    protected_dir.chmod(stat.S_IREAD | stat.S_IEXEC)  # read and execute, but not write
    pushd(protected_dir)

    project_dir = protected_dir.joinpath("test_project")

    with pytest.raises(
        ProjectInitServiceError,
        match=f"Permission denied to create '{project_dir}'",
    ):
        ProjectInitService(project_dir).init(activate=False, add_discovery=False)


def test_project_init_missing_parent_directory(tmp_path: Path, pushd):
    if platform.system() == "Windows":
        pytest.xfail(
            "Windows can't remove a directory that is in use. See https://docs.python.org/3/library/os.html#os.remove"
        )

    missing_dir = tmp_path.joinpath("missing")
    missing_dir.mkdir()
    pushd(missing_dir)

    project_dir = missing_dir.joinpath("test_project")
    missing_dir.rmdir()  # remove the parent directory

    with pytest.raises(
        ProjectInitServiceError,
        match=f"Could not create directory '{project_dir}'.",
    ):
        ProjectInitService(project_dir).init(activate=False, add_discovery=False)
