from __future__ import annotations

import os
import platform
import re
import subprocess

import mock
import pytest

from meltano.core.project import Project
from meltano.core.venv_service import PLATFORM_SPECS, VenvService, VirtualEnv


class TestVenvService:
    @pytest.fixture
    def subject(self, project):
        return VenvService(project, "namespace", "name")

    def test_clean_run_files(self, project: Project, subject: VenvService):
        file = project.run_dir("name", "test.file.txt")
        file.touch()
        assert file.exists() and file.is_file()

        subject.clean_run_files()
        assert not file.exists()

    @pytest.mark.asyncio
    async def test_clean_install(self, project, subject: VenvService):
        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
            )

        await subject.install(["example"], clean=True)
        venv_dir = subject.project.venvs_dir("namespace", "name")

        # ensure the venv is created
        assert venv_dir.exists()

        # ensure that the binary is python3
        assert os.path.samefile(
            venv_dir.joinpath("bin/python"), venv_dir.joinpath("bin/python3")
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

    @pytest.mark.asyncio
    async def test_install(self, project, subject: VenvService):
        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
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

    @pytest.mark.asyncio
    async def test_requires_clean_install(self, project, subject: VenvService):
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


class TestVirtualEnv:
    @pytest.mark.parametrize("system", ["Linux", "Darwin", "Windows"])
    def test_cross_platform(self, system, project):
        with mock.patch("platform.system", return_value=system):
            subject = VirtualEnv(project.venvs_dir("pytest", "pytest"))
            assert subject.specs == PLATFORM_SPECS[system]

    def test_unknown_platform(self, project):
        with mock.patch("platform.system", return_value="commodore64"), pytest.raises(
            Exception, match="(?i)Platform 'commodore64'.*?not supported."
        ):
            VirtualEnv(project.venvs_dir("pytest", "pytest"))
