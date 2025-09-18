from __future__ import annotations

import platform
import typing as t

import dotenv
import pytest

from meltano.core.plugin import PluginRef, PluginType
from meltano.core.plugin.command import UndefinedEnvVarError
from meltano.core.plugin_invoker import (
    ExecutableNotFoundError,
    PluginExecutionError,
    UnknownCommandError,
)
from meltano.core.tracking.contexts import environment_context
from meltano.core.venv_service import VirtualEnv

if t.TYPE_CHECKING:
    from meltano.core.plugin_invoker import PluginInvoker


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
    async def test_unknown_command(self, plugin_invoker) -> None:
        with pytest.raises(UnknownCommandError) as exc_info:
            await plugin_invoker.invoke_async(command="foo")

        assert isinstance(exc_info.value, UnknownCommandError)
        assert exc_info.value.command == "foo"
        assert "supports the following commands" in str(exc_info.value)

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

    @pytest.mark.asyncio
    async def test_executable_not_found_error(
        self,
        plugin_invoker: PluginInvoker,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that ExecutableNotFoundError is raised when executable is missing."""
        import asyncio

        from meltano.core.plugin_invoker import ExecutableNotFoundError

        # Mock asyncio.create_subprocess_exec to raise FileNotFoundError
        # for the executable
        async def mock_create_subprocess_exec(*args: t.Any, **kwargs: t.Any):  # noqa: ARG001
            error = FileNotFoundError(
                2, "No such file or directory", "/path/to/missing-executable"
            )
            raise error

        monkeypatch.setattr(
            asyncio, "create_subprocess_exec", mock_create_subprocess_exec
        )

        # Mock exec_args to return our test executable path
        monkeypatch.setattr(
            plugin_invoker,
            "exec_args",
            lambda *args, **kwargs: ["/path/to/missing-executable", "arg1", "arg2"],  # noqa: ARG005
        )

        with pytest.raises(ExecutableNotFoundError) as exc_info:
            await plugin_invoker.invoke_async()

        # Verify the error message contains information about the executable
        error_msg = str(exc_info.value)
        assert "could not be found" in error_msg
        assert plugin_invoker.plugin.name in error_msg

    @pytest.mark.asyncio
    async def test_plugin_execution_error(
        self,
        plugin_invoker: PluginInvoker,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that PluginExecutionError is raised when plugin can't access files."""
        import asyncio

        from meltano.core.plugin_invoker import PluginExecutionError

        # Mock asyncio.create_subprocess_exec to raise FileNotFoundError for
        # a different file
        async def mock_create_subprocess_exec(*args: t.Any, **kwargs: t.Any):  # noqa: ARG001
            error = FileNotFoundError(
                2,
                "No such file or directory",
                "/project/data/missing-file",
            )
            raise error

        monkeypatch.setattr(
            asyncio,
            "create_subprocess_exec",
            mock_create_subprocess_exec,
        )

        # Mock exec_args to return a different executable path
        monkeypatch.setattr(
            plugin_invoker,
            "exec_args",
            lambda *args, **kwargs: ["/usr/bin/existing-executable", "arg1", "arg2"],  # noqa: ARG005
        )

        with pytest.raises(PluginExecutionError) as exc_info:
            await plugin_invoker.invoke_async()

        # Verify the error message indicates execution failure, not missing executable
        error_msg = str(exc_info.value)
        assert "execution failed" in error_msg
        assert "/project/data/missing-file" in error_msg
        assert plugin_invoker.plugin.name in error_msg

    def test_executable_not_found_error_class(self) -> None:
        """Test ExecutableNotFoundError class directly."""
        plugin = PluginRef(PluginType.EXTRACTORS, "test-tap")
        error = ExecutableNotFoundError(plugin, "missing-executable")

        error_msg = str(error)
        assert "Executable 'missing-executable' could not be found" in error_msg
        assert "Extractor 'test-tap'" in error_msg
        assert "meltano install extractor test-tap" in error_msg

    def test_plugin_execution_error_class(self) -> None:
        """Test PluginExecutionError class directly."""
        plugin = PluginRef(PluginType.TRANSFORMERS, "dbt")
        original_error = (
            "[Errno 2] No such file or directory: '/project/transform/dbt_project.yml'"
        )
        error = PluginExecutionError(plugin, original_error)

        error_msg = str(error)
        assert "Transformer 'dbt' execution failed:" in error_msg
        assert "/project/transform/dbt_project.yml" in error_msg
        # Should not suggest installation since it's not an executable issue
        assert "meltano install" not in error_msg
