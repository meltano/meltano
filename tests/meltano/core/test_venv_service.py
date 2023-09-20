from __future__ import annotations

import os
import platform
import re
import subprocess
import sys

import mock
import pytest

from meltano.core.error import MeltanoError
from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_install_service import install_pip_plugin
from meltano.core.project import Project
from meltano.core.venv_service import VenvService, VirtualEnv


def _check_venv_created_with_python(project: Project, python: str | None):
    with mock.patch(
        "meltano.core.venv_service.VirtualEnv._resolve_python_path",
    ) as venv_mock:
        VenvService(project=project)
        venv_mock.assert_called_once_with(python)


async def _check_venv_created_with_python_for_plugin(
    project: Project,
    plugin: ProjectPlugin,
    python: str | None,
):
    with mock.patch(
        "meltano.core.venv_service.VirtualEnv._resolve_python_path",
    ) as venv_mock, mock.patch("meltano.core.venv_service.VenvService.install"):
        await install_pip_plugin(project=project, plugin=plugin)
        venv_mock.assert_called_once_with(python)


class TestVenvService:
    @pytest.fixture()
    def subject(self, project):
        return VenvService(project=project, namespace="namespace", name="name")

    def test_clean_run_files(self, project: Project, subject: VenvService):
        file = project.run_dir("name", "test.file.txt")
        file.touch()
        assert file.exists()
        assert file.is_file()

        subject.clean_run_files()
        assert not file.exists()

    @pytest.mark.asyncio()
    @pytest.mark.usefixtures("project")
    async def test_clean_install(self, subject: VenvService):
        if platform.system() == "Windows":
            pytest.xfail(
                "Fails on Windows: https://github.com/meltano/meltano/issues/3444",
            )

        await subject.install(["example"], clean=True)
        venv_dir = subject.project.venvs_dir("namespace", "name")

        # ensure the venv is created
        assert venv_dir.exists()

        # ensure that the binary is python3
        assert os.path.samefile(
            venv_dir.joinpath("bin/python"),
            venv_dir.joinpath("bin/python3"),
        )

        # ensure that the package is installed
        run = subprocess.run(
            [venv_dir.joinpath("bin/python"), "-m", "pip", "list"],
            check=True,
            capture_output=True,
        )
        assert re.search(r"example\s+0\.1\.0", str(run.stdout))

        # ensure that pip is the latest version
        run = subprocess.run(
            [venv_dir.joinpath("bin/python"), "-m", "pip", "list", "--outdated"],
            check=True,
            capture_output=True,
        )
        for line in str(run.stdout).splitlines():
            assert not line.startswith("pip ")

        assert subject.exec_path("some_exe").parts[-6:] == (
            ".meltano",
            "namespace",
            "name",
            "venv",
            "bin",
            "some_exe",
        )

        # ensure a fingerprint file was created
        with open(venv_dir / ".meltano_plugin_fingerprint") as fingerprint_file:
            assert (
                fingerprint_file.read()
                # sha256 of "example"
                == "50d858e0985ecc7f60418aaf0cc5ab587f42c2570a884095a9e8ccacd0f6545c"
            )

        # ensure that log file was created and is not empty
        assert subject.pip_log_path.exists()
        assert subject.pip_log_path.is_file()
        assert subject.pip_log_path.stat().st_size > 0

    @pytest.mark.asyncio()
    @pytest.mark.usefixtures("project")
    async def test_install(self, subject: VenvService):
        if platform.system() == "Windows":
            pytest.xfail(
                "Fails on Windows: https://github.com/meltano/meltano/issues/3444",
            )

        # Make sure the venv exists already
        await subject.install(["example"], clean=True)
        venv_dir = subject.project.venvs_dir("namespace", "name")

        # remove the package, then check that after a regular install the package exists
        run = subprocess.run(
            [
                venv_dir.joinpath("bin/python"),
                "-m",
                "pip",
                "uninstall",
                "--yes",
                "example",
            ],
            check=True,
            capture_output=True,
        )

        await subject.install(["example"])

        # ensure that the package is installed
        run = subprocess.run(
            [venv_dir.joinpath("bin/python"), "-m", "pip", "list"],
            check=True,
            capture_output=True,
        )
        assert re.search(r"example\s+0\.1\.0", str(run.stdout))

    @pytest.mark.asyncio()
    @pytest.mark.usefixtures("project")
    async def test_requires_clean_install(self, subject: VenvService):
        # Make sure the venv exists already
        await subject.install(["example"], clean=True)

        if platform.system() != "Windows":
            python_path = subject.exec_path("python")
            original_link_target = os.readlink(python_path)
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

    def test_top_level_python_setting(self, project: Project):
        project.settings.set("python", "test-python-executable-project-level")
        _check_venv_created_with_python(project, "test-python-executable-project-level")
        project.settings.unset("python")
        _check_venv_created_with_python(project, None)

    async def test_plugin_python_setting(self, project: Project):
        plugin = ProjectPlugin(
            PluginType.EXTRACTORS,
            name="tap-mock",
            python="test-python-executable-plugin-level",
        )

        await _check_venv_created_with_python_for_plugin(
            project,
            plugin,
            "test-python-executable-plugin-level",
        )

        # Setting the project-level `python` setting should have no effect at first
        # because the plugin-level setting takes precedence.
        project.settings.set("python", "test-python-executable-project-level")

        await _check_venv_created_with_python_for_plugin(
            project,
            plugin,
            "test-python-executable-plugin-level",
        )

        # The project-level setting should have an effect after the plugin-level
        # setting is unset
        plugin = ProjectPlugin(PluginType.EXTRACTORS, name="tap-mock")

        await _check_venv_created_with_python_for_plugin(
            project,
            plugin,
            "test-python-executable-project-level",
        )

        project.settings.unset("python")

        # After both the project-level and plugin-level are unset, it should be None
        await _check_venv_created_with_python_for_plugin(project, plugin, None)


class TestVirtualEnv:
    @pytest.mark.parametrize(
        ("system", "lib_dir"),
        (
            ("Linux", "lib"),
            ("Darwin", "lib"),
            ("Windows", "Lib"),
        ),
    )
    def test_cross_platform(self, system: str, lib_dir: str, project: Project):
        with mock.patch("platform.system", return_value=system):
            subject = VirtualEnv(project.venvs_dir("pytest", "pytest"))
            assert subject.lib_dir == subject.root / lib_dir

    def test_unknown_platform(self, project: Project):
        with mock.patch("platform.system", return_value="commodore64"), pytest.raises(
            MeltanoError,
            match="(?i)Platform 'commodore64'.*?not supported.",
        ):
            VirtualEnv(project.venvs_dir("pytest", "pytest"))

    def test_different_python_versions(self, project: Project):
        root = project.venvs_dir("pytest", "pytest")

        assert (
            VirtualEnv(root, python=None).python_path
            == VirtualEnv(root).python_path
            == VirtualEnv(root, python=sys.executable).python_path
            == sys.executable
        )

        with mock.patch(
            "shutil.which",
            return_value="/usr/bin/test-python-executable",
        ), mock.patch("os.access", return_value=True):
            assert (
                VirtualEnv(root, python="test-python-executable").python_path
                == "/usr/bin/test-python-executable"
            )

        with mock.patch("os.path.exists", return_value=True), mock.patch(
            "os.access",
            return_value=True,
        ):
            assert (
                VirtualEnv(
                    root,
                    python="/usr/bin/test-python-executable",
                ).python_path
                == "/usr/bin/test-python-executable"
            )

        with mock.patch(
            "shutil.which",
            return_value="/usr/bin/test-python-executable",
        ), mock.patch(
            "os.access",
            return_value=False,
        ), pytest.raises(
            MeltanoError,
            match="'/usr/bin/test-python-executable' is not executable",
        ):
            VirtualEnv(root, python="test-python-executable")

        with pytest.raises(
            MeltanoError,
            match="Python executable 'test-python-executable' was not found",
        ):
            VirtualEnv(root, python="test-python-executable")
