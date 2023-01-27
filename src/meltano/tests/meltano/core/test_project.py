from __future__ import annotations

import platform
import threading
import time
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool

import pytest

from meltano.core.behavior.versioned import IncompatibleVersionError
from meltano.core.project import PROJECT_ROOT_ENV, Project, ProjectNotFound


@pytest.fixture
def deactivate_project(project):
    Project.deactivate()
    yield
    Project.activate(project)


def update(payload):
    project = Project.find()

    with project.meltano_update() as meltano:
        for k, v in payload.items():
            setattr(meltano, k, v)


class IndefiniteThread(threading.Thread):
    """Never ending thread."""

    def __init__(self):
        """Set stop event."""
        super().__init__()
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self, *args, **kwargs):
        while not self._stop_event.is_set():
            self.do(*args, **kwargs)


class ProjectReader(IndefiniteThread):
    """Project using a never ending thread."""

    def __init__(self, project):
        """Set the project."""
        self.project = project
        super().__init__()

    def do(self):
        assert self.project.meltano
        time.sleep(50 / 1000)  # 50ms


class TestProject:
    @pytest.mark.usefixtures("deactivate_project")
    def test_find(self, project, tmp_path, monkeypatch):
        # defaults to the cwd
        found = Project.find(activate=False)
        assert found == project

        # or you can specify a path
        found = Project.find(project.root, activate=False)
        assert found == project

        # or set the MELTANO_PROJECT_ROOT env var
        with monkeypatch.context() as ctx1:
            ctx1.chdir(project.root.joinpath("extract"))
            ctx1.setenv(PROJECT_ROOT_ENV, "..")

            found = Project.find(activate=False)
            assert found == project

        # it can also recurse up from a subdirectory
        with monkeypatch.context() as ctx2:
            ctx2.chdir(project.root.joinpath("extract"))
            found = Project.find(activate=False)
            assert found == project

        # and it fails if there isn't a meltano.yml
        with pytest.raises(ProjectNotFound):
            Project.find(tmp_path)

    def test_activate(self, project):
        Project.deactivate()
        assert Project._default is None

        Project.activate(project)

        assert Project._default is project
        assert Project.find() is project

    def test_find_threadsafe(self, project, concurrency):
        workers = ThreadPool(concurrency["threads"])
        projects = workers.map(Project.find, range(concurrency["cases"]))
        assert all(x is project for x in projects)

    @pytest.mark.concurrent
    def test_meltano_concurrency(self, project, concurrency):
        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
            )

        payloads = [{f"test_{i}": i} for i in range(1, concurrency["cases"] + 1)]

        reader = ProjectReader(project)
        reader.start()

        workers = Pool(concurrency["processes"])
        workers.map(update, payloads)

        reader.stop()
        reader.join()

        meltano = project.meltano
        unpacked_items = (item for payload in payloads for item in payload.items())
        for key, val in unpacked_items:
            assert meltano.extras[key] == val

    def test_preserve_comments(self, project: Project):
        original_contents = project.meltanofile.read_text()

        new_contents = f"# Please don't delete me :)\n{original_contents}"
        project.meltanofile.write_text(new_contents)

        with project.meltano_update() as meltano:
            meltano.extras["a_new_key"] = "New Key"

        contents = project.meltanofile.read_text()
        assert contents.startswith("# Please don't delete me :)\n")
        assert "a_new_key: New Key" in contents


class TestIncompatibleProject:
    def test_incompatible(self, project):
        with project.meltano_update() as meltano:
            meltano["version"] += 1

        with pytest.raises(IncompatibleVersionError):
            Project.activate(project)
