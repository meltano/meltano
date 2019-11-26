import pytest
import yaml
import os
import shutil
import threading
import time

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
        for k, v in payload.items():
            setattr(meltano, k, v)


class IndefiniteThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self, *args, **kwargs):
        while not self._stop_event.is_set():
            self.do(*args, **kwargs)


class ProjectReader(IndefiniteThread):
    def __init__(self, project):
        self.project = project
        super().__init__()

    def do(self):
        assert self.project.meltano
        time.sleep(50 / 1000)  # 50ms


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

    @pytest.mark.concurrent
    def test_meltano_concurrency(self, project, concurrency):
        payloads = [{f"test_{i}": i} for i in range(1, concurrency["cases"] + 1)]

        reader = ProjectReader(project)
        reader.start()

        workers = Pool(concurrency["processes"])
        workers.map(update, payloads)

        reader.stop()
        reader.join()

        meltano = project.meltano
        for key, val in ((k, v) for payload in payloads for k, v in payload.items()):
            assert meltano[key] == val


class TestIncompatibleProject:
    def test_incompatible(self, project):
        with project.meltano_update() as meltano:
            meltano["version"] += 1

        with pytest.raises(IncompatibleVersionError):
            Project.activate(project)
