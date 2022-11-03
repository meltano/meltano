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
        "existing directory",
    ),
)
def test_project_init_success(create_project_dir: bool, tmp_path: Path, pushd):
    projects_dir = tmp_path.joinpath("success")
    projects_dir.mkdir()
    pushd(projects_dir)

    project_dir = projects_dir.joinpath("test_project")

    ProjectInitService(project_dir.relative_to(Path.cwd())).init(
        activate=False, add_discovery=False
    )

    shutil.rmtree(project_dir)

    if create_project_dir:
        project_dir.mkdir()

    ProjectInitService(project_dir.absolute()).init(activate=False, add_discovery=False)


def test_project_init_existing_directory_file_conflict(tmp_path: Path, pushd):
    projects_dir = tmp_path.joinpath("file_conflict")
    projects_dir.mkdir()
    pushd(projects_dir)

    project_dir = projects_dir.joinpath("test_project")
    project_dir.mkdir()
    project_dir.joinpath("README.md").write_text("")

    with pytest.raises(ProjectInitServiceError) as e:
        ProjectInitService(project_dir).init(activate=False, add_discovery=False)

    assert e.match("Could not create project 'test_project'")
    assert e.match(re.escape("Found 1 conflicting file: test_project/README.md"))


def test_project_init_existing_directory_existing_project_subdirectory_no_write_permissions(
    tmp_path: Path, pushd
):
    projects_dir = tmp_path.joinpath("file_conflict")
    projects_dir.mkdir()
    pushd(projects_dir)

    project_dir = projects_dir.joinpath("test_project")
    project_dir.mkdir()

    extract_dir = project_dir.joinpath("extract")
    extract_dir.mkdir()
    extract_dir.chmod(stat.S_IREAD | stat.S_IEXEC)  # read and execute, but not write

    with pytest.raises(ProjectInitServiceError) as e:
        ProjectInitService(project_dir).init(activate=False, add_discovery=False)

    assert e.match("Could not create project 'test_project'")
    assert e.match(
        re.escape("Found 1 directory with no write permissions: test_project/extract")
    )


def test_project_init_existing_directory_multiple_check_errors(tmp_path: Path, pushd):
    projects_dir = tmp_path.joinpath("file_conflict")
    projects_dir.mkdir()
    pushd(projects_dir)

    project_dir = projects_dir.joinpath("test_project")
    project_dir.mkdir()
    project_dir.joinpath("README.md").write_text("")
    project_dir.joinpath("requirements.txt").write_text("")

    extract_dir = project_dir.joinpath("extract")
    extract_dir.mkdir()
    extract_dir.joinpath(".gitkeep").write_text("")
    extract_dir.chmod(stat.S_IREAD | stat.S_IEXEC)  # read and execute, but not write

    extract_dir = project_dir.joinpath("load")
    extract_dir.mkdir()
    extract_dir.joinpath(".gitkeep").write_text("")
    extract_dir.chmod(stat.S_IREAD | stat.S_IEXEC)  # read and execute, but not write

    extract_dir = project_dir.joinpath("transform")
    extract_dir.mkdir()
    extract_dir.joinpath(".gitkeep").write_text("")
    extract_dir.chmod(stat.S_IREAD | stat.S_IEXEC)  # read and execute, but not write

    with pytest.raises(ProjectInitServiceError) as e:
        ProjectInitService(project_dir).init(activate=False, add_discovery=False)

    assert e.match("Could not create project 'test_project'")
    assert e.match("Found 5 conflicting files: ")
    assert e.match("Found 3 directories with no write permissions: ")


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
        match="Permission denied to create 'test_project'",
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

    with pytest.raises(
        ProjectInitServiceError,
        match="Could not create directory 'test_project'.",
    ):
        project_init_service = ProjectInitService(project_dir)
        missing_dir.rmdir()  # remove the parent directory

        project_init_service.init(activate=False, add_discovery=False)
