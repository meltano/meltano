import pytest
import yaml
import os
import shutil

from meltano.core.project import Project, ProjectNotFound


class TestProject:
    def test_find(self, project, mkdtemp):
        # cd into a nested directory
        found = Project.find(project.root.joinpath("model"))

        assert found == project

        with pytest.raises(ProjectNotFound):
            try:
                empty_dir = mkdtemp("meltano_empty_project")
                Project.find(empty_dir)
            finally:
                shutil.rmtree(empty_dir)

    def test_activate(self, project):
        assert os.getenv("MELTANO_PROJECT") is None

        with open(".env", "w") as env:
            env.write(f"MELTANO_PROJECT={project.root}")

        project.activate()
        assert os.getenv("MELTANO_PROJECT") == str(project.root)
