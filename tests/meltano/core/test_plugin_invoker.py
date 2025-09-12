from __future__ import annotations

import json
import platform
import shutil
from unittest import mock

import dotenv
import pytest

from meltano.core.plugin.command import UndefinedEnvVarError
from meltano.core.plugin_invoker import UnknownCommandError
from meltano.core.tracking.contexts import environment_context
from meltano.core.venv_service import VirtualEnv


class TestPluginInvoker:
    @pytest.fixture
    async def plugin_invoker(self, utility, session, plugin_invoker_factory):
        subject = plugin_invoker_factory(utility)
        async with subject.prepared(session):
            yield subject

    @pytest.fixture
    async def nonpip_plugin_invoker(self, nonpip_tap, session, plugin_invoker_factory):
        subject = plugin_invoker_factory(nonpip_tap)
        async with subject.prepared(session):
            yield subject

    @pytest.mark.asyncio
    async def test_env(self, project, tap, session, plugin_invoker_factory) -> None:
        project.dotenv.touch()
        dotenv.set_key(project.dotenv, "DUMMY_ENV_VAR", "from_dotenv")
        dotenv.set_key(project.dotenv, "TAP_MOCK_TEST", "from_dotenv")
        project.refresh()

        subject = plugin_invoker_factory(tap)
        async with subject.prepared(session):
            env = subject.env()

        # .env
        assert env["DUMMY_ENV_VAR"] == "from_dotenv"

        # Project env
        assert env["MELTANO_PROJECT_ROOT"] == str(project.root)
        assert env["MELTANO_ENVIRONMENT"] == ""

        # Project settings
        assert env["MELTANO_CLI_LOG_LEVEL"] == "info"

        # Plugin info
        assert env["MELTANO_EXTRACTOR_NAME"] == tap.name

        # Plugin settings
        assert env["MELTANO_EXTRACT_TEST"] == env["TAP_MOCK_TEST"] == "from_dotenv"
        assert env["MELTANO_EXTRACT__SELECT"] == env["TAP_MOCK__SELECT"] == '["*.*"]'

        # Plugin execution environment
        venv = VirtualEnv(project.venvs_dir(tap.type, tap.name))
        assert env["VIRTUAL_ENV"] == str(venv.root)
        assert env["PATH"].startswith(str(venv.bin_dir))
        assert "PYTHONPATH" not in env

        assert (
            env["MELTANO_PARENT_CONTEXT_UUID"]
            == environment_context.data["context_uuid"]
        )

    @pytest.mark.asyncio
    async def test_environment_env(
        self,
        project_with_environment,
        tap,
        session,
        plugin_invoker_factory,
    ) -> None:
        subject = plugin_invoker_factory(tap)
        async with subject.prepared(session):
            env = subject.env()

        # Project env
        assert env["MELTANO_ENVIRONMENT"] == project_with_environment.environment.name

    @pytest.mark.asyncio
    async def test_expanded_environment_env(
        self,
        project_with_environment,
        tap,
        session,
        plugin_invoker_factory,
    ) -> None:
        if platform.system() == "Windows":
            pytest.xfail(
                "Fails on Windows: https://github.com/meltano/meltano/issues/3444",
            )
        subject = plugin_invoker_factory(tap)
        async with subject.prepared(session):
            env = subject.env()

        assert env["ENVIRONMENT_ENV_VAR"] == str(
            project_with_environment.root / "file.txt",
        )

    @pytest.mark.asyncio
    async def test_env_from_manifest_success(
        self,
        project,
        tap,
        session,
        plugin_invoker_factory,
    ) -> None:
        # Create a mock manifest file
        manifest_dir = project.root / ".meltano" / "manifests"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_file = manifest_dir / "meltano-manifest.json"

        manifest_data = {
            "env": {"PROJECT_VAR": "project_value"},
            "plugins": {
                "extractors": [
                    {
                        "name": "tap-mock",
                        "env": {
                            "TAP_MOCK_API_KEY": "manifest_key",
                            "TAP_MOCK_ENDPOINT": "https://manifest.example.com",
                        },
                    }
                ]
            },
        }

        with manifest_file.open("w") as f:
            json.dump(manifest_data, f)

        subject = plugin_invoker_factory(tap)
        async with subject.prepared(session):
            env = subject.env()

        # Verify manifest env vars are present
        assert env["PROJECT_VAR"] == "project_value"
        assert env["TAP_MOCK_API_KEY"] == "manifest_key"
        assert env["TAP_MOCK_ENDPOINT"] == "https://manifest.example.com"

        # Verify runtime env vars still work
        assert env["MELTANO_EXTRACTOR_NAME"] == tap.name
        assert "VIRTUAL_ENV" in env

    @pytest.mark.asyncio
    async def test_env_fallback_when_no_manifest(
        self,
        project,
        tap,
        session,
        plugin_invoker_factory,
    ) -> None:
        # Ensure no manifest exists
        manifest_dir = project.root / ".meltano" / "manifests"
        if manifest_dir.exists():
            shutil.rmtree(manifest_dir)

        # Mock compile_manifest to fail
        with mock.patch(
            "meltano.core.manifest.loader.compile_manifest"
        ) as mock_compile:
            mock_compile.side_effect = Exception("Compilation failed")

            subject = plugin_invoker_factory(tap)
            async with subject.prepared(session):
                env = subject.env()

            # Should still have env vars from original implementation
            assert env["MELTANO_EXTRACTOR_NAME"] == tap.name
            assert env["MELTANO_PROJECT_ROOT"] == str(project.root)
            assert (
                env["MELTANO_EXTRACT__SELECT"] == env["TAP_MOCK__SELECT"] == '["*.*"]'
            )

    @pytest.mark.asyncio
    async def test_env_plugin_not_in_manifest(
        self,
        project,
        tap,
        session,
        plugin_invoker_factory,
    ) -> None:
        # Create manifest without our plugin
        manifest_dir = project.root / ".meltano" / "manifests"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_file = manifest_dir / "meltano-manifest.json"

        manifest_data = {
            "env": {"PROJECT_VAR": "project_value"},
            "plugins": {"extractors": []},  # Empty list
        }

        with manifest_file.open("w") as f:
            json.dump(manifest_data, f)

        subject = plugin_invoker_factory(tap)
        async with subject.prepared(session):
            env = subject.env()

        # Should fall back to original implementation
        # The warning is logged by structlog which outputs to stdout, not to caplog
        # We just need to verify that it falls back to the original implementation
        # by checking that we have the expected env vars
        assert env["MELTANO_EXTRACTOR_NAME"] == tap.name
        # Should have the normal env vars from settings
        assert env["MELTANO_EXTRACT__SELECT"] == env["TAP_MOCK__SELECT"] == '["*.*"]'

    @pytest.mark.asyncio
    async def test_env_manifest_override_precedence(
        self,
        project,
        tap,
        session,
        plugin_invoker_factory,
    ) -> None:
        # Create a mock manifest file with overlapping env vars
        manifest_dir = project.root / ".meltano" / "manifests"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_file = manifest_dir / "meltano-manifest.json"

        manifest_data = {
            "env": {"PROJECT_VAR": "project_value", "SHARED_VAR": "project_shared"},
            "plugins": {
                "extractors": [
                    {
                        "name": "tap-mock",
                        "env": {
                            "SHARED_VAR": "plugin_shared",  # Should override project
                            "TAP_MOCK_CUSTOM": "custom_value",
                        },
                    }
                ]
            },
        }

        with manifest_file.open("w") as f:
            json.dump(manifest_data, f)

        # Also set a dotenv var
        project.dotenv.touch()
        dotenv.set_key(project.dotenv, "SHARED_VAR", "dotenv_shared")
        project.refresh()

        subject = plugin_invoker_factory(tap)
        async with subject.prepared(session):
            env = subject.env()

        # Verify precedence: dotenv should override manifest
        assert env["SHARED_VAR"] == "dotenv_shared"
        assert env["PROJECT_VAR"] == "project_value"
        assert env["TAP_MOCK_CUSTOM"] == "custom_value"

    @pytest.mark.asyncio
    async def test_unknown_command(self, plugin_invoker) -> None:
        with pytest.raises(UnknownCommandError) as err:
            await plugin_invoker.invoke_async(command="foo")

        assert err.value.command == "foo"
        assert "supports the following commands" in str(err.value)

    def test_expand_exec_args(self, plugin_invoker) -> None:
        exec_args = plugin_invoker.exec_args(
            "extra",
            "args",
            command="cmd",
            env={
                "ENV_VAR_ARG": "env-var-arg",
            },
        )

        assert exec_args[0].endswith("utility-mock")
        assert exec_args[1:] == ["--option", "env-var-arg", "extra", "args"]

    def test_expand_command_exec_args(self, plugin_invoker) -> None:
        exec_args = plugin_invoker.exec_args(
            "extra",
            "args",
            command="cmd",
            env={
                "ENV_VAR_ARG": "env-var-arg",
            },
        )

        assert exec_args[0].endswith("utility-mock")
        assert exec_args[1:] == ["--option", "env-var-arg", "extra", "args"]

    @pytest.mark.asyncio
    async def test_undefined_env_var(self, plugin_invoker) -> None:
        with pytest.raises(UndefinedEnvVarError) as err:
            await plugin_invoker.invoke_async(command="cmd")

        assert (
            "Command 'cmd' referenced unset environment "
            "variable '$ENV_VAR_ARG' in an argument"
        ) in str(err.value)

    def test_alternate_command_executable(self, plugin_invoker) -> None:
        exec_args = plugin_invoker.exec_args(
            "extra",
            "args",
            command="alternate-exec",
            env={
                "ENV_VAR_ARG": "env-var-arg",
            },
        )

        assert exec_args[0].endswith("other-utility")
        assert exec_args[1:] == ["--option", "env-var-arg", "extra", "args"]

    @pytest.mark.parametrize(
        ("executable_str", "assert_fn"),
        (
            ("tap-test", lambda exe, _: exe == "tap-test"),
            ("./tap-test", lambda exe, name: exe.endswith(f"{name}/tap-test")),
            ("/apps/tap-test", lambda exe, _: exe == "/apps/tap-test"),
        ),
    )
    @pytest.mark.asyncio
    async def test_expand_nonpip_command_exec_args(
        self,
        nonpip_plugin_invoker,
        session,
        executable_str,
        assert_fn,
    ) -> None:
        if platform.system() == "Windows":
            pytest.xfail(
                "Fails on Windows: https://github.com/meltano/meltano/issues/3444",
            )
        nonpip_plugin_invoker.plugin.executable = executable_str
        exec_args = nonpip_plugin_invoker.exec_args()

        assert assert_fn(exec_args[0], nonpip_plugin_invoker.project.root)

        await nonpip_plugin_invoker.prepare(session)
        env = nonpip_plugin_invoker.env()

        assert "VIRTUAL_ENV" not in env
        assert "PYTHONPATH" not in env
