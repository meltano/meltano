from __future__ import annotations

import os
from pathlib import Path

import yaml

from meltano.core import bundle
from meltano.core.project import Project

from .file import FilePlugin


class MeltanoFilePlugin(FilePlugin):

    overwrite = {"meltano.yml"}

    def __init__(self, discovery: bool = False):
        super().__init__(None, None)
        self._discovery = discovery

    def file_contents(self, project) -> dict[Path, str]:
        """Get a mapping of paths to contents.

        Args:
            project: The Meltano project:

        Returns:
            A mapping.
        """
        initialize_file = bundle.root / "initialize.yml"
        file_contents = {
            Path(relative_path): content
            for relative_path, content in yaml.safe_load(initialize_file.open()).items()
        }
        if self._discovery:
            file_contents["discovery.yml"] = (bundle.root / "discovery.yml").read_text()
        return file_contents

    def update_config(self, project):
        return {}

    def files_to_create(
        self,
        project: Project,
        paths_to_update: list[str],
    ) -> dict[Path, str]:
        """Return the contents of the files to be created in the project.

        Args:
            project: The Meltano project.
            paths_to_update: The paths of the files to be updated.

        Returns:
            A dictionary of file names and their contents.
        """
        return self.project_file_contents(project, paths_to_update)

    def project_file_contents(
        self,
        project: Project,
        paths_to_update: list[str],
    ) -> dict[Path, str]:
        """Return the contents of the files to be created or updated in the project.

        Args:
            project: The Meltano project.
            paths_to_update: The paths of the files to be updated.

        Returns:
            A dictionary of file names and their contents.
        """
        return self.file_contents(project)

    def write_file(
        self,
        project: Project,
        relative_path: os.PathLike,
        content: str,
    ) -> bool:
        """Write the file to the project.

        Args:
            project: The Meltano project.
            relative_path: The relative path of the file.
            content: The contents of the file.

        Returns:
            True if the file was written, False otherwise.
        """
        project_path = project.root_dir(relative_path)
        if project_path.exists() and not any(
            project_path.match(path) for path in self.overwrite
        ):
            return False

        project_path.parent.mkdir(parents=True, exist_ok=True)
        project_path.write_text(content)

        return True
