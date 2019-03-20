import pytest
import yaml
import os
import shutil

from meltano.core.project import Project, ProjectNotFound


class TestProject:
    def test_find(self, project, mkdtemp):
        # defaults to the cwd
        found = Project.find()
        assert found == project

        # or you can specify a path
        found = Project.find(project.root)
        assert found == project

        # but it doens't recurse up, you have to be
        # at the meltano.yml level
        with pytest.raises(ProjectNotFound):
            Project.find(project.root.joinpath("model"))

        # and it fails if there isn't a meltano.yml
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
