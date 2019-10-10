import pytest
import yaml
import os
import shutil
import threading

from meltano.core.project import Project, ProjectNotFound
from meltano.core.behavior.versioned import IncompatibleVersionError
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool


@pytest.fixture
def deactivate_project(project):
    Project._default = None
    yield
    Project._default = project


def update(payload):
    project = Project.find()

    with project.meltano_update() as meltano:
        meltano.update(payload)


class TestProject:
    @pytest.mark.usefixtures("deactivate_project")
    def test_find(self, project, mkdtemp):
        # defaults to the cwd
        found = Project.find(activate=False)
        assert found == project

        # or you can specify a path
        found = Project.find(project.root, activate=False)
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

        # `Project.find()` always return the default instance
        Project.activate(project)
        assert os.getenv("MELTANO_PROJECT") == str(project.root)
        assert Project.find() is project

    def test_find_threadsafe(self, project, concurrency):
        workers = ThreadPool(concurrency["threads"])
        projects = workers.map(Project.find, range(concurrency["cases"]))

        assert all(map(lambda x: x is project, projects))

    def test_meltano_concurrency(self, project, concurrency):
        payloads = [{f"test_{i}": i} for i in range(concurrency["cases"])]

        workers = Pool(concurrency["processes"])
        workers.map(update, payloads)

        for key, val in ((k, v) for payload in payloads for k, v in payload.items()):
            print(project.meltano)
            assert project.meltano[key] == val, str(project.meltano)


class TestIncompatibleProject:
    def test_incompatible(self, project):
        with project.meltano_update() as meltano:
            meltano["version"] += 1

        with pytest.raises(IncompatibleVersionError):
            Project.activate(project)
