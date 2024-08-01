"""Shared Pytest fixture utilities."""

from __future__ import annotations

import logging
import os
import typing as t
from contextlib import contextmanager

from meltano.core.project import Project
from meltano.core.project_init_service import ProjectInitService

if t.TYPE_CHECKING:
    from pathlib import Path


@contextmanager
def cd(path: Path) -> Path:
    prev_dir = os.getcwd()
    os.chdir(path)
    try:
        yield path
    finally:
        os.chdir(prev_dir)


@contextmanager
def tmp_project(name: str, source: Path, compatible_copy_tree) -> Project:
    project_init_service = ProjectInitService(name)
    blank_project = project_init_service.init()
    logging.debug(f"Created new project at {blank_project.root}")  # noqa: G004, TID251
    os.remove(blank_project.meltanofile)
    compatible_copy_tree(source, blank_project.root)
    Project._default = None
    project = Project(blank_project.root)
    with cd(project.root):
        try:
            project.refresh()
            yield project
        finally:
            Project.deactivate()
            logging.debug(f"Cleaned project at {project.root}")  # noqa: G004, TID251
