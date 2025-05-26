from __future__ import annotations

import platform
import sys
import typing as t
from importlib.util import module_from_spec, spec_from_file_location
from unittest import mock
from unittest.mock import AsyncMock

import pytest

from meltano.core.plugin import PluginType
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.plugin_invoker import asyncio

if t.TYPE_CHECKING:
    from pathlib import Path
    from types import ModuleType

    from meltano.core.plugin.superset import SupersetInvoker


def load_module_from_path(name: str, path: Path) -> ModuleType:
    """Load a module given its name and filesystem path.

    Replacement for the deprecated `imp.load_source`.

    Args:
        name: The name of the module as it would be in `sys.modules`.
        path: The path of the `.py` file.

    Returns:
        The imported module.
    """
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class TestSuperset:
    @pytest.fixture(scope="class")
    def subject(self, project_add_service):
        with mock.patch.object(PluginInstallService, "install_plugin"):
            return project_add_service.add(PluginType.UTILITIES, "superset")

    @pytest.mark.asyncio
    @pytest.mark.filterwarnings(
        "ignore:Unknown setting 'SUPERSET_WEBSERVER_PORT':RuntimeWarning",
    )
    async def test_hooks(
        self,
        subject,
        project,
        session,
        plugin_invoker_factory,
        monkeypatch,
    ) -> None:
        if platform.system() == "Windows":
            pytest.xfail(
                "Fails on Windows: https://github.com/meltano/meltano/issues/3444",
            )
        run_dir = project.run_dir("superset")
        config_path = run_dir.joinpath("superset_config.py")

        handle_mock = mock.Mock()
        handle_mock.name = subject.name
        handle_mock.wait = AsyncMock(return_value=0)
        handle_mock.returncode = 0

        original_exec = asyncio.create_subprocess_exec

        def popen_mock(cmd, *popen_args, **kwargs):
            assert kwargs["env"]["SUPERSET_HOME"] == str(run_dir)
            assert kwargs["env"]["SUPERSET_CONFIG_PATH"] == str(config_path)

            # first time, it creates the `superset.db`
            if {"db", "upgrade"}.issubset(popen_args):
                project.plugin_dir(subject, "superset.db").touch()
            # second time, it inits
            elif "init" in popen_args:  # noqa: SIM114
                return handle_mock
            # third time, it runs the requested command
            elif "--version" in popen_args:
                return handle_mock
            else:
                return original_exec(cmd, *popen_args, **kwargs)
            return handle_mock

        with (
            mock.patch.object(
                asyncio,
                "create_subprocess_exec",
                side_effect=popen_mock,
            ) as popen,
            mock.patch("meltano.core.plugin_invoker.PluginConfigService.configure"),
        ):
            invoker: SupersetInvoker = plugin_invoker_factory(subject)
            # This ends up calling the hooks
            async with invoker.prepared(session):
                await invoker.invoke_async("--version")

                commands = [
                    popen_args
                    for _, popen_args, kwargs in popen.mock_calls
                    if popen_args and isinstance(popen_args, tuple)
                ]
                assert commands[0][1] == "db"
                assert commands[0][2] == "upgrade"
                assert commands[1][1] == "init"
                assert commands[2][1] == "--version"

                assert config_path.exists()
                assert project.plugin_dir(subject, "superset.db").exists()

                config_module = load_module_from_path("superset_config", config_path)

                config_keys = dir(config_module)
                assert "SQLALCHEMY_DATABASE_URI" in config_keys
                assert (
                    f"sqlite:///{project.plugin_dir(subject, 'superset.db')}"
                    == config_module.SQLALCHEMY_DATABASE_URI
                )
                assert "SECRET_KEY" in config_keys

            # Test custom setting
            invoker.settings_service.set("SUPERSET_WEBSERVER_PORT", 5000)

            # Test config_path extra
            custom_config_filename = "custom_superset_config.py"
            custom_config_path = project.root.joinpath(custom_config_filename)
            custom_config_path.write_text('FOO_FAKE_SETTING = "fake_value"')
            monkeypatch.setitem(
                invoker.settings_service.config_override,
                "_config_path",
                custom_config_filename,
            )

            async with invoker.prepared(session):
                await invoker.invoke_async("--version")

                config_module = load_module_from_path("superset_config", config_path)

                config_keys = dir(config_module)
                # Verify default Meltano-managed settings are here
                assert "SQLALCHEMY_DATABASE_URI" in config_keys
                assert "SECRET_KEY" in config_keys
                # Verify custom Meltano-managed settings are here
                assert "SUPERSET_WEBSERVER_PORT" in config_keys
                assert config_module.SUPERSET_WEBSERVER_PORT == 5000
                # Verify settings from the custom config path are here
                assert "FOO_FAKE_SETTING" in config_keys
                assert config_module.FOO_FAKE_SETTING == "fake_value"

            assert not run_dir.joinpath("superset_config.py").exists()

    @pytest.mark.asyncio
    async def test_before_cleanup(self, subject, plugin_invoker_factory) -> None:
        invoker: SupersetInvoker = plugin_invoker_factory(subject)

        assert not invoker.files["config"].exists()

        # No exception should be raised even though the file doesn't exist
        await invoker.cleanup()
