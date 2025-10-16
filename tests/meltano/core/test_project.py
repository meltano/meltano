from __future__ import annotations

import platform
import threading
import time
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool

import pytest

from meltano.core.error import ProjectNotFound
from meltano.core.project import PROJECT_ROOT_ENV, Project
from meltano.core.utils import IncompatibleMeltanoVersionError, get_meltano_version


@pytest.fixture
def deactivate_project(project):
    Project.deactivate()
    yield
    Project.activate(project)


def update(payload: dict) -> None:
    project = Project.find()

    with project.meltano_update() as meltano:
        for k, v in payload.items():
            setattr(meltano, k, v)


class IndefiniteThread(threading.Thread):
    """Never ending thread."""

    def __init__(self) -> None:
        """Set stop event."""
        super().__init__()
        self._stop_event = threading.Event()

    def stop(self) -> None:
        self._stop_event.set()

    def run(self, *args, **kwargs) -> None:
        while not self._stop_event.is_set():
            self.do(*args, **kwargs)


class ProjectReader(IndefiniteThread):
    """Project using a never ending thread."""

    def __init__(self, project) -> None:
        """Set the project."""
        self.project = project
        super().__init__()

    def do(self) -> None:
        assert self.project.meltano
        time.sleep(50 / 1000)  # 50ms


class TestProject:
    @pytest.mark.usefixtures("deactivate_project")
    def test_find(self, project, tmp_path, monkeypatch) -> None:
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

    def test_activate(self, project) -> None:
        Project.deactivate()
        assert Project._default is None

        Project.activate(project)

        assert Project._default is project
        assert Project.find() is project

    def test_find_threadsafe(self, project, concurrency) -> None:
        with ThreadPool(concurrency["threads"]) as workers:
            projects = workers.map(Project.find, range(concurrency["cases"]))
            assert all(x is project for x in projects)

    @pytest.mark.xfail(
        platform.system() == "Windows",
        reason="Fails on Windows: https://github.com/meltano/meltano/issues/3444",
        run=True,
        strict=True,
    )
    @pytest.mark.concurrent
    def test_meltano_concurrency(self, project, concurrency) -> None:
        payloads = [{f"test_{i}": i} for i in range(1, concurrency["cases"] + 1)]

        reader = ProjectReader(project)
        reader.start()

        with Pool(concurrency["processes"]) as pool:
            pool.map(update, payloads)
            reader.stop()
            reader.join()

            pool.close()
            pool.join()

        meltano = project.meltano
        unpacked_items = (item for payload in payloads for item in payload.items())
        for key, val in unpacked_items:
            assert meltano.extras[key] == val

    def test_preserve_comments(self, project: Project) -> None:
        original_contents = project.meltanofile.read_text()

        new_contents = f"# Please don't delete me :)\n{original_contents}"
        project.meltanofile.write_text(new_contents)

        with project.meltano_update() as meltano:
            meltano.extras["a_new_key"] = "New Key"

        contents = project.meltanofile.read_text()
        assert contents.startswith("# Please don't delete me :)\n")
        assert "a_new_key: New Key" in contents


class TestIncompatibleProject:
    @pytest.fixture
    def increase_requires_meltano(self, project):
        with project.meltano_update() as meltano:
            meltano["requires_meltano"] = "==999.0.0"
        yield
        with project.meltano_update() as meltano:
            meltano["requires_meltano"] = None

    @pytest.fixture
    def set_compatible_meltano(self, project):
        with project.meltano_update() as meltano:
            current = get_meltano_version()
            meltano["requires_meltano"] = f"=={current}"
        yield
        with project.meltano_update() as meltano:
            meltano["requires_meltano"] = None

    @pytest.mark.usefixtures("increase_requires_meltano")
    def test_incompatible_requires_meltano(self, project) -> None:
        with pytest.raises(IncompatibleMeltanoVersionError):
            Project.activate(project)

    @pytest.mark.usefixtures("set_compatible_meltano")
    def test_compatible_requires_meltano(self, project) -> None:
        Project.activate(project)
