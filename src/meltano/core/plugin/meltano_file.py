from __future__ import annotations  # noqa: D100

import typing as t
from pathlib import Path

import yaml

from meltano.core import bundle
from meltano.core.plugin.file import FilePlugin

if t.TYPE_CHECKING:
    import os

    from meltano.core.project import Project


class MeltanoFilePlugin(FilePlugin):  # noqa: D101
    overwrite: t.ClassVar[set[str]] = {"meltano.yml"}

    def __init__(self) -> None:
        """Initialize the MeltanoFilePlugin."""
        super().__init__(None, None)

    def file_contents(
        self,
        project,  # noqa: ANN001, ARG002
    ) -> dict[Path, str]:
        """Get a mapping of paths to contents.

        Args:
            project: The Meltano project:

        Returns:
            A mapping.
        """
        with bundle.root.joinpath("initialize.yml").open() as f:
            return {
                Path(relative_path): content
                for relative_path, content in yaml.safe_load(f).items()
            }

    def update_config(self, project):  # noqa: ANN001, ANN201, ARG002, D102
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
        paths_to_update: list[str],  # noqa: ARG002
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
