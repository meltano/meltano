from __future__ import annotations

import platform

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
    async def test_env(self, project, tap, session, plugin_invoker_factory):
        project.dotenv.touch()
        dotenv.set_key(project.dotenv, "DUMMY_ENV_VAR", "from_dotenv")
        dotenv.set_key(project.dotenv, "TAP_MOCK_TEST", "from_dotenv")

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
        self, project_with_environment, tap, session, plugin_invoker_factory
    ):
        subject = plugin_invoker_factory(tap)
        async with subject.prepared(session):
            env = subject.env()

        # Project env
        assert (
            env["MELTANO_ENVIRONMENT"]
            == project_with_environment.active_environment.name
        )

    @pytest.mark.asyncio
    async def test_expanded_environment_env(
        self, project_with_environment, tap, session, plugin_invoker_factory
    ):
        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
            )
        subject = plugin_invoker_factory(tap)
        async with subject.prepared(session):
            env = subject.env()

        assert env["ENVIRONMENT_ENV_VAR"] == str(
            project_with_environment.root / "file.txt"
        )

    @pytest.mark.asyncio
    async def test_unknown_command(self, plugin_invoker):
        with pytest.raises(UnknownCommandError) as err:
            await plugin_invoker.invoke_async(command="foo")

        assert err.value.command == "foo"
        assert "supports the following commands" in str(err.value)

    def test_expand_exec_args(self, plugin_invoker):
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

    def test_expand_command_exec_args(self, plugin_invoker):
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
    async def test_undefined_env_var(self, plugin_invoker):
        with pytest.raises(UndefinedEnvVarError) as err:
            await plugin_invoker.invoke_async(command="cmd")

        assert (
            "Command 'cmd' referenced unset environment variable '$ENV_VAR_ARG' in an argument"
            in str(err.value)
        )

    def test_alternate_command_executable(self, plugin_invoker):
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
        "executable_str,assert_fn",
        [
            ("tap-test", lambda exe, name: exe == "tap-test"),
            ("./tap-test", lambda exe, name: exe.endswith(f"{name}/tap-test")),
            ("/apps/tap-test", lambda exe, name: exe == "/apps/tap-test"),
        ],
    )
    @pytest.mark.asyncio
    async def test_expand_nonpip_command_exec_args(
        self, nonpip_plugin_invoker, session, executable_str, assert_fn
    ):
        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
            )
        nonpip_plugin_invoker.plugin.executable = executable_str
        exec_args = nonpip_plugin_invoker.exec_args()

        assert assert_fn(exec_args[0], nonpip_plugin_invoker.project.root)

        await nonpip_plugin_invoker.prepare(session)
        env = nonpip_plugin_invoker.env()

        assert "VIRTUAL_ENV" not in env
        assert "PYTHONPATH" not in env
