"""Shared Pytest fixture utilities."""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from pathlib import Path

from meltano.core.project import Project
from meltano.core.project_init_service import ProjectInitService


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
    project = project_init_service.init(add_discovery=False)
    logging.debug(f"Created new project at {project.root}")
    os.remove(project.meltanofile)
    compatible_copy_tree(source, project.root)
    with cd(project.root):
        try:
            yield project
        finally:
            Project.deactivate()
            logging.debug(f"Cleaned project at {project.root}")
