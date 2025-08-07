"""Shared Pytest fixture utilities."""

from __future__ import annotations

import logging
import os
import typing as t
from contextlib import contextmanager
from pathlib import Path

from meltano.core.project import Project
from meltano.core.project_init_service import ProjectInitService

if t.TYPE_CHECKING:
    from collections.abc import Generator


@contextmanager
def cd(path: Path) -> Generator[Path, None, None]:
    prev_dir = Path.cwd()
    os.chdir(path)
    try:
        yield path
    finally:
        os.chdir(prev_dir)


@contextmanager
def tmp_project(
    name: str,
    source: Path,
    compatible_copy_tree,
) -> Generator[Project, None, None]:
    project_init_service = ProjectInitService(name)
    blank_project = project_init_service.init()
    logging.debug(f"Created new project at {blank_project.root}")  # noqa: G004
    blank_project.meltanofile.unlink()
    compatible_copy_tree(source, blank_project.root)
    Project._default = None
    project = Project(blank_project.root)
    with cd(project.root):
        try:
            project.refresh()
            yield project
        finally:
            Project.deactivate()
            logging.debug(f"Cleaned project at {project.root}")  # noqa: G004
