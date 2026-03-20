from __future__ import annotations

import platform
import subprocess
import sys
import typing as t
from asyncio.subprocess import Process
from unittest import mock

import pytest

from meltano.core.error import AsyncSubprocessError
from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.venv_service import (
    UvBackend,
    VirtualEnv,
    VirtualenvBackend,
    VirtualEnvService,
    fingerprint,
)

if t.TYPE_CHECKING:
    from pathlib import Path

    from meltano.core.project import Project


def test_fingerprint_with_python_path():
    """Test that fingerprint includes Python path when provided."""
    import sys

    pip_args = ["package==1.0.0", "another-package"]

    fp1 = fingerprint(pip_args)
    fp2 = fingerprint(pip_args, "/usr/bin/python3.11")

    assert fp1 != fp2

    fp3 = fingerprint(pip_args, "/usr/bin/python3.11")
    assert fp2 == fp3

    fp4 = fingerprint(pip_args, "/usr/bin/python3.12")
    assert fp2 != fp4

    fp5 = fingerprint(pip_args, None)
    assert fp1 == fp5

    # Test that sys.executable doesn't change fingerprint
    fp6 = fingerprint(pip_args, sys.executable)
    assert fp1 == fp6


class TestVirtualEnv:
    @pytest.mark.parametrize(
        ("system", "lib_dir"),
        (
            ("Linux", "lib"),
            ("Darwin", "lib"),
            ("Windows", "Lib"),
        ),
    )
    def test_cross_platform(self, system: str, lib_dir: str, tmp_path: Path) -> None:
        with mock.patch("platform.system", return_value=system):
            subject = VirtualEnv(tmp_path / "venv")
            assert subject.lib_dir == subject.root / lib_dir

    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="subprocess is not called on Windows",
    )
    @pytest.mark.asyncio
    async def test_site_packages(self, tmp_path: Path) -> None:
        proc = subprocess.CompletedProcess([], returncode=0, stdout=b"3 99 42")
        with mock.patch("subprocess.run", return_value=proc):
            subject = VirtualEnv(tmp_path / "venv", python="python3.9")
            assert subject.site_packages_dir.parts[-2:] == (
                "python3.99",
                "site-packages",
            )


@pytest.fixture
def venv(tmp_path: Path) -> VirtualEnv:
    return VirtualEnv(tmp_path / "venv")


@pytest.fixture
def log_path(tmp_path: Path) -> Path:
    return tmp_path / "install.log"


class TestVirtualEnvService:
    @pytest.fixture(params=["virtualenv", "uv"])
    def subject(
        self,
        request: pytest.FixtureRequest,
        project: Project,
        venv: VirtualEnv,
        log_path: Path,
    ) -> VirtualEnvService:
        backend_name = request.param
        backend_class = UvBackend if backend_name == "uv" else VirtualenvBackend
        return VirtualEnvService(
            project=project,
            namespace="namespace",
            name="name",
            backend=backend_class(venv=venv, log_path=log_path),
        )

    def test_clean_run_files(
        self,
        project: Project,
        subject: VirtualEnvService,
    ) -> None:
        run_dir = project.dirs.run("name")

        file = run_dir / "test.file.txt"
        file.touch()

        assert file.exists()
        assert file.is_file()

        sub_dir = run_dir / "test_dir"
        sub_dir.mkdir()

        assert sub_dir.exists()
        assert sub_dir.is_dir()

        subject.clean_run_files()

        assert not file.exists()
        assert not sub_dir.exists()
        assert run_dir.exists(), (
            "Expected all files in the run dir to be removed, but not the dir itself"
        )

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="chmod behavior is different on Windows",
    )
    async def test_create_venv_dir_not_writable(
        self, subject: VirtualEnvService
    ) -> None:
        venv_dir = subject.venv.root
        venv_dir.mkdir()
        # Don't allow writing to the venv dir
        venv_dir.chmod(0o555)

        with pytest.raises(
            AsyncSubprocessError,
            match="Could not create the virtualenv for",
        ) as excinfo:
            await subject.create()

        assert (
            "Permission denied" in await excinfo.value.stderr  # uv's message
            or "is not write-able" in await excinfo.value.stderr  # virtualenv's message
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("project")
    async def test_clean_install(self, subject: VirtualEnvService) -> None:
        if platform.system() == "Windows":
            pytest.xfail(
                "Fails on Windows: https://github.com/meltano/meltano/issues/3444",
            )

        # Pre-create a venv with a marker file to ensure `clean=True` clears it
        venv_dir = subject.venv.root
        venv_dir.mkdir()
        marker_file = venv_dir / "pre_existing_marker.txt"
        marker_file.write_text("marker")

        await subject.install(["example"], clean=True)

        # ensure the venv is created and previous contents have been cleared
        assert venv_dir.exists()
        assert not marker_file.exists()

        # ensure that the binary is python3
        assert (venv_dir / "bin/python").samefile(venv_dir / "bin/python3")

        # ensure that the package is installed
        installed = await subject._backend.list_installed()
        assert any(dep["name"] == "example" for dep in installed)

        # ensure that pip is the latest version
        outdated = await subject._backend.list_installed("--outdated")
        assert not any(dep["name"] == "pip" for dep in outdated)

        assert subject.venv.exec_path("some_exe").parts[-3:] == (
            "venv",
            "bin",
            "some_exe",
        )

        # ensure a fingerprint file was created
        fingerprint_content = (venv_dir / ".meltano_plugin_fingerprint").read_text()
        expected_fingerprint = fingerprint(["example"], subject.venv.python_path)
        assert fingerprint_content == expected_fingerprint

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("project")
    async def test_install(self, subject: VirtualEnvService, log_path: Path) -> None:
        # Make sure the venv exists already
        await subject.install(["cowsay"], clean=True)

        # remove the package, then check that after a regular install the package exists
        await subject._backend.uninstall_package("cowsay")
        await subject.install(["cowsay"])

        installed = await subject._backend.list_installed()
        assert any(dep["name"] == "cowsay" for dep in installed)

        if isinstance(subject._backend, VirtualenvBackend):
            assert log_path.exists()  # noqa: ASYNC240
            assert log_path.is_file()  # noqa: ASYNC240
            assert log_path.stat().st_size > 0  # noqa: ASYNC240

    async def test_handle_installation_error(self, subject: VirtualEnvService) -> None:
        process = mock.Mock(spec=Process)
        process.stderr = "Some error"

        with (
            mock.patch(
                "meltano.core.venv_service.VirtualEnvService.pip_install",
                side_effect=AsyncSubprocessError("Something went wrong", process),
            ),
            pytest.raises(
                AsyncSubprocessError,
                match="Something went wrong",
            ),
        ):
            await subject.install(["cowsay"])

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("project")
    async def test_requires_clean_install(self, subject: VirtualEnvService) -> None:
        # Make sure the venv exists already
        await subject.create()
        subject.venv.write_fingerprint(["example"])

        if platform.system() != "Windows":
            python_path = subject.venv.exec_path("python")
            original_link_target = python_path.readlink()
            try:
                # Simulate the deletion of the underlying Python executable by
                # making its symlink point to a file that does not exist
                python_path.unlink()
                python_path.symlink_to("./fake/path/to/python/executable")
                assert subject.requires_clean_install(["example"])
            finally:
                # Restore the symlink to the actual Python executable
                python_path.unlink()
                python_path.symlink_to(original_link_target)

        assert not subject.requires_clean_install(["example"])
        assert subject.requires_clean_install(["example==0.1.0"])
        assert subject.requires_clean_install(["example", "another-package"])

    @pytest.mark.asyncio
    async def test_requires_clean_install_python_change(
        self,
        subject: VirtualEnvService,
    ) -> None:
        await subject.install(["example"], clean=True)
        assert not subject.requires_clean_install(["example"])

        original_python = subject.venv.python_path
        subject.venv.python_path = "/fake/test/python"
        assert subject.requires_clean_install(["example"])

        subject.venv.python_path = original_python
        assert not subject.requires_clean_install(["example"])


class TestVenvBackend:
    @pytest.mark.parametrize("backend", ("virtualenv", "uv"))
    async def test_python_setting(self, project: Project, backend: str) -> None:
        cls = UvBackend if backend == "uv" else VirtualenvBackend

        plugin_python = "test-python-executable-plugin-level"
        plugin = ProjectPlugin(
            PluginType.EXTRACTORS,
            name="tap-mock",
            python=plugin_python,
        )
        subject = cls.from_plugin(project, plugin)
        assert subject.venv.python_path == plugin_python

        # Setting the project-level `python` setting should have no effect at first
        # because the plugin-level setting takes precedence.
        project_python = "test-python-executable-project-level"
        project.settings.set("python", project_python)
        subject = cls.from_plugin(project, plugin)
        assert subject.venv.python_path == plugin_python

        # The project-level setting should have an effect after the plugin-level
        # setting is unset
        plugin = ProjectPlugin(PluginType.EXTRACTORS, name="tap-mock")
        subject = cls.from_plugin(project, plugin)
        assert subject.venv.python_path == project_python

        # After both the project-level and plugin-level are unset, the system Python
        # should be used
        project.settings.unset("python")
        subject = cls.from_plugin(project, plugin)
        assert subject.venv.python_path == sys.executable
