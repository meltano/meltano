from __future__ import annotations

import platform
import sys
import typing as t
from asyncio.subprocess import Process
from pathlib import Path
from unittest import mock

import pytest

from meltano.core.error import AsyncSubprocessError, MeltanoError
from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_install_service import install_pip_plugin
from meltano.core.venv_service import UvVenvService, VenvService, VirtualEnv, find_uv

if t.TYPE_CHECKING:
    from meltano.core.project import Project


class TestVenvService:
    cls = VenvService

    def _check_venv_created_with_python(
        self,
        project: Project,
        python: str | None,
    ) -> None:
        with mock.patch("meltano.core.venv_service._resolve_python_path") as venv_mock:
            self.cls(project=project)
            venv_mock.assert_called_once_with(python)

    async def _check_venv_created_with_python_for_plugin(
        self,
        project: Project,
        plugin: ProjectPlugin,
        python: str | None,
    ) -> None:
        with (
            mock.patch(
                "meltano.core.venv_service._resolve_python_path",
            ) as venv_mock,
            mock.patch("meltano.core.venv_service.VenvService.install"),
        ):
            await install_pip_plugin(project=project, plugin=plugin)
            venv_mock.assert_called_once_with(python)

    def assert_pip_log_file(self, service: VenvService):
        assert service.pip_log_path.exists()
        assert service.pip_log_path.is_file()
        assert service.pip_log_path.stat().st_size > 0

    @pytest.fixture
    def subject(self, project):
        return VenvService(project=project, namespace="namespace", name="name")

    def test_clean_run_files(self, project: Project, subject: VenvService) -> None:
        run_dir = project.run_dir("name")

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
    async def test_create_venv_dir_not_writable(
        self, project: Project, request: pytest.FixtureRequest
    ) -> None:
        plugin_type = "dummy_type"
        plugin_name = request.node.name

        venv_service = VenvService(
            project=project,
            namespace=plugin_type,
            name=plugin_name,
        )
        venv_dir = project.venvs_dir(plugin_type, plugin_name, make_dirs=True)
        # Don't allow writing to the venv dir
        venv_dir.chmod(0o555)

        with pytest.raises(
            AsyncSubprocessError,
            match="Could not create the virtualenv for",
        ) as excinfo:
            await venv_service.create()

        assert "is not write-able" in await excinfo.value.stderr

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("project")
    async def test_clean_install(self, subject: VenvService) -> None:
        if platform.system() == "Windows":
            pytest.xfail(
                "Fails on Windows: https://github.com/meltano/meltano/issues/3444",
            )

        await subject.install(["example"], clean=True)
        venv_dir = subject.project.venvs_dir("namespace", "name")

        # ensure the venv is created
        assert venv_dir.exists()

        # ensure that the binary is python3
        assert (venv_dir / "bin/python").samefile(venv_dir / "bin/python3")

        # ensure that the package is installed
        installed = await subject.list_installed()
        assert any(dep["name"] == "example" for dep in installed)

        # ensure that pip is the latest version
        outdated = await subject.list_installed("--outdated")
        assert not any(dep["name"] == "pip " for dep in outdated)

        assert subject.exec_path("some_exe").parts[-6:] == (
            ".meltano",
            "namespace",
            "name",
            "venv",
            "bin",
            "some_exe",
        )

        # ensure a fingerprint file was created
        fingerprint = (venv_dir / ".meltano_plugin_fingerprint").read_text()
        assert (
            fingerprint
            # sha256 of "example"
            == "50d858e0985ecc7f60418aaf0cc5ab587f42c2570a884095a9e8ccacd0f6545c"
        )

        # ensure that log file was created and is not empty
        self.assert_pip_log_file(subject)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("project")
    async def test_install(self, subject: VenvService) -> None:
        if platform.system() == "Windows":
            pytest.xfail(
                "Fails on Windows: https://github.com/meltano/meltano/issues/3444",
            )

        # Make sure the venv exists already
        await subject.install(["example"], clean=True)

        # remove the package, then check that after a regular install the package exists
        await subject.uninstall_package("example")
        await subject.install(["example"])

        # ensure that the package is installed
        installed = await subject.list_installed()
        assert any(dep["name"] == "example" for dep in installed)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("project")
    async def test_requires_clean_install(self, subject: VenvService) -> None:
        # Make sure the venv exists already
        await subject.install(["example"], clean=True)

        if platform.system() != "Windows":
            python_path = subject.exec_path("python")
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

    def test_top_level_python_setting(self, project: Project) -> None:
        project.settings.set("python", "test-python-executable-project-level")
        self._check_venv_created_with_python(
            project,
            "test-python-executable-project-level",
        )
        project.settings.unset("python")
        self._check_venv_created_with_python(project, None)

    async def test_plugin_python_setting(self, project: Project) -> None:
        plugin = ProjectPlugin(
            PluginType.EXTRACTORS,
            name="tap-mock",
            python="test-python-executable-plugin-level",
        )

        await self._check_venv_created_with_python_for_plugin(
            project,
            plugin,
            "test-python-executable-plugin-level",
        )

        # Setting the project-level `python` setting should have no effect at first
        # because the plugin-level setting takes precedence.
        project.settings.set("python", "test-python-executable-project-level")

        await self._check_venv_created_with_python_for_plugin(
            project,
            plugin,
            "test-python-executable-plugin-level",
        )

        # The project-level setting should have an effect after the plugin-level
        # setting is unset
        plugin = ProjectPlugin(PluginType.EXTRACTORS, name="tap-mock")

        await self._check_venv_created_with_python_for_plugin(
            project,
            plugin,
            "test-python-executable-project-level",
        )

        project.settings.unset("python")

        # After both the project-level and plugin-level are unset, it should be None
        await self._check_venv_created_with_python_for_plugin(project, plugin, None)


class TestVirtualEnv:
    cls = VirtualEnv

    async def _check_venv_created_with_python_for_plugin(
        self,
        project: Project,
        plugin: ProjectPlugin,
        python: str | None,
    ) -> None:
        with (
            mock.patch(
                "meltano.core.venv_service._resolve_python_path",
            ) as venv_mock,
            mock.patch("meltano.core.venv_service.UvVenvService.install"),
        ):
            await install_pip_plugin(project=project, plugin=plugin)
            venv_mock.assert_called_once_with(python)

    @pytest.mark.parametrize(
        ("system", "lib_dir"),
        (
            ("Linux", "lib"),
            ("Darwin", "lib"),
            ("Windows", "Lib"),
        ),
    )
    def test_cross_platform(self, system: str, lib_dir: str, project: Project) -> None:
        with mock.patch("platform.system", return_value=system):
            subject = self.cls(project.venvs_dir("pytest", "pytest"))
            assert subject.lib_dir == subject.root / lib_dir

    def test_unknown_platform(self, project: Project) -> None:
        with (
            mock.patch("platform.system", return_value="commodore64"),
            pytest.raises(
                MeltanoError,
                match="(?i)Platform 'commodore64'.*?not supported.",
            ),
        ):
            self.cls(project.venvs_dir("pytest", "pytest"))

    def test_different_python_versions(self, project: Project) -> None:
        root = project.venvs_dir("pytest", "pytest")

        assert (
            self.cls(root, python=None).python_path
            == self.cls(root).python_path
            == self.cls(root, python=sys.executable).python_path
            == sys.executable
        )

        with (
            mock.patch(
                "shutil.which",
                return_value="/usr/bin/test-python-executable",
            ),
            mock.patch("os.access", return_value=True),
        ):
            assert (
                self.cls(root, python="test-python-executable").python_path
                == "/usr/bin/test-python-executable"
            )

        with (
            mock.patch("os.path.exists", return_value=True),
            mock.patch(
                "os.access",
                return_value=True,
            ),
        ):
            path_str = "/usr/bin/test-python-executable"
            venv = self.cls(root, python=path_str)
            assert venv.python_path == path_str

            venv = self.cls(root, python=Path(path_str))
            assert venv.python_path == str(Path(path_str).resolve())

        with (
            mock.patch(
                "shutil.which",
                return_value="/usr/bin/test-python-executable",
            ),
            mock.patch("os.access", return_value=False),
            pytest.raises(
                MeltanoError,
                match="'/usr/bin/test-python-executable' is not executable",
            ),
        ):
            self.cls(root, python="test-python-executable")

        with pytest.raises(
            MeltanoError,
            match="Python executable 'test-python-executable' was not found",
        ):
            self.cls(root, python="test-python-executable")

        with pytest.raises(
            MeltanoError,
            match="not the number 3.11",
        ):
            self.cls(root, python=3.11)


class TestUvVenvService(TestVenvService):
    def assert_pip_log_file(self, service: VenvService):
        pass

    @pytest.fixture
    def subject(self, project):
        find_uv.cache_clear()
        return UvVenvService(project=project, namespace="namespace", name="name")

    def test_find_uv_builtin(self, monkeypatch: pytest.MonkeyPatch) -> None:
        find_uv.cache_clear()
        monkeypatch.setattr("uv.find_uv_bin", lambda: "/usr/bin/uv")
        assert find_uv() == "/usr/bin/uv"

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("project")
    async def test_install(self, subject: UvVenvService) -> None:
        # Make sure the venv exists already
        await subject.install(["cowsay"], clean=True)

        # remove the package, then check that after a regular install the package exists
        await subject.uninstall_package("cowsay")
        await subject.install(["cowsay"])

        installed = await subject.list_installed()
        assert any(dep["name"] == "cowsay" for dep in installed)

    async def test_handle_installation_error(self, subject: UvVenvService) -> None:
        process = mock.Mock(spec=Process)
        process.stderr = "Some error"

        with (
            mock.patch(
                "meltano.core.venv_service.UvVenvService.install_pip_args",
                side_effect=AsyncSubprocessError("Something went wrong", process),
            ),
            pytest.raises(
                AsyncSubprocessError,
                match="Failed to install plugin 'name'",
            ),
        ):
            await subject.install(["cowsay"])
