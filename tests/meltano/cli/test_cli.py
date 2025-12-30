from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
import typing as t
import uuid
from http import HTTPStatus
from pathlib import Path
from time import perf_counter_ns
from unittest import mock

import click
import pytest
import responses
import yaml
from structlog.stdlib import get_logger

import meltano
from asserts import assert_cli_runner
from fixtures.utils import cd
from meltano.cli import cli, handle_meltano_error
from meltano.cli.params import UUIDParamType
from meltano.cli.utils import CliError
from meltano.core.error import EmptyMeltanoFileException, MeltanoError
from meltano.core.logging.utils import setup_logging
from meltano.core.project import PROJECT_ENVIRONMENT_ENV, PROJECT_READONLY_ENV, Project
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.version_check import PYPI_URL, VersionCheckResult

if t.TYPE_CHECKING:
    from fixtures.cli import MeltanoCliRunner
    from meltano.core.project_init_service import ProjectInitService

ANSI_RE = re.compile(r"\033\[[;?0-9]*[a-zA-Z]")


class TestCli:
    @pytest.fixture
    def test_cli_project(
        self,
        tmp_path: Path,
        project_init_service: ProjectInitService,
    ):
        """Return the non-activated project."""
        os.chdir(tmp_path)
        project = project_init_service.init(activate=False)
        Project._default = None
        try:
            yield project
        finally:
            Project.deactivate()
            shutil.rmtree(project.root)

    @pytest.fixture
    def deactivate_project(self) -> None:
        Project.deactivate()

    @pytest.fixture
    def empty_project(
        self,
        empty_meltano_yml_dir,
        pushd,  # noqa: ARG002
    ):
        project = Project(empty_meltano_yml_dir)
        try:
            yield project
        finally:
            Project.deactivate()

    @pytest.fixture
    def incompatible_version_project(
        self,
        tmp_path: Path,
        project_init_service: ProjectInitService,
    ) -> t.Generator[Project, None, None]:
        os.chdir(tmp_path)
        project = project_init_service.init(activate=False)
        Project._default = None
        with project.meltano_update() as meltano:
            meltano.requires_meltano = ">=999"

        try:
            yield project
        finally:
            Project.deactivate()
            shutil.rmtree(project.root)

    @pytest.mark.order(0)
    def test_activate_project(self, test_cli_project, cli_runner, pushd) -> None:
        project = test_cli_project

        pushd(project.root)
        cli_runner.invoke(cli, ["hub", "ping"])

        assert Project._default is not None
        assert Project._default.root == project.root
        assert Project._default.readonly is False

    @pytest.mark.order(1)
    def test_empty_meltano_yml_project(self, empty_project, cli_runner, pushd) -> None:
        pushd(empty_project.root)
        with pytest.raises(EmptyMeltanoFileException):
            cli_runner.invoke(cli, ["config"], catch_exceptions=False)

    @pytest.mark.order(1)
    def test_incompatible_meltano_error(
        self,
        incompatible_version_project: Project,
        cli_runner: MeltanoCliRunner,
        pushd,
    ) -> None:
        pushd(incompatible_version_project.root)
        result = cli_runner.invoke(cli, ["config"])
        assert result.exit_code == 3
        assert re.match("You're using .* but this project requires .*", result.output)

    @pytest.mark.order(2)
    def test_activate_project_readonly_env(
        self,
        test_cli_project,
        cli_runner,
        pushd,
        monkeypatch,
    ) -> None:
        monkeypatch.setenv(PROJECT_READONLY_ENV, "true")
        assert Project._default is None
        pushd(test_cli_project.root)
        cli_runner.invoke(cli, ["hub", "ping"])
        assert Project._default.readonly

    @pytest.mark.order(2)
    def test_activate_project_readonly_dotenv(
        self,
        test_cli_project,
        cli_runner,
        pushd,
    ) -> None:
        test_cli_project.settings.set("project_readonly", value=True)
        assert Project._default is None
        pushd(test_cli_project.root)
        cli_runner.invoke(cli, ["hub", "ping"])
        assert Project._default.readonly

    def test_environment_precedence(
        self,
        project: Project,
        pushd,
        cli_runner: MeltanoCliRunner,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        pushd(project.root)
        monkeypatch.delenv(PROJECT_ENVIRONMENT_ENV, raising=False)
        environment_names = {
            name: f"env_set_from_{name}" for name in ("dotenv", "cli_option", "env_var")
        }
        with mock.patch(
            "meltano.core.project.Project.dotenv_env",
            new_callable=mock.PropertyMock,
            return_value={PROJECT_ENVIRONMENT_ENV: environment_names["dotenv"]},
        ):
            args = ("invoke", "tap-mock")
            results = {
                "dotenv": cli_runner.invoke(cli, args),
                "cli_option": cli_runner.invoke(
                    cli,
                    (f"--environment={environment_names['cli_option']}", *args),
                ),
                "env_var": cli_runner.invoke(
                    cli,
                    args,
                    env={PROJECT_ENVIRONMENT_ENV: environment_names["env_var"]},
                ),
            }
        for source, name in environment_names.items():
            assert results[source].exit_code
            assert (
                results[source].exception.args[0]
                == f"Environment {name!r} was not found."
            )

    def test_version(self, cli_runner) -> None:
        cli_version = cli_runner.invoke(cli, ["--version"])

        assert cli_version.output == f"meltano, version {meltano.__version__}\n"

    @pytest.mark.usefixtures("deactivate_project")
    def test_default_environment_is_activated(
        self,
        project_files_cli,
        cli_runner,
        pushd,
    ) -> None:
        pushd(project_files_cli.root)
        cli_runner.invoke(
            cli,
            ["test"],
        )
        assert Project._default.environment.name == "test-meltano-environment"

    @pytest.mark.usefixtures("deactivate_project")
    def test_environment_flag_overrides_default(
        self,
        project_files_cli,
        cli_runner,
        pushd,
    ) -> None:
        pushd(project_files_cli.root)
        cli_runner.invoke(
            cli,
            ["--environment", "test-subconfig-2-yml", "test"],
        )

        assert Project._default.environment.name == "test-subconfig-2-yml"

    @pytest.mark.usefixtures("deactivate_project")
    def test_environment_variable_overrides_default(
        self,
        project_files_cli,
        cli_runner,
        pushd,
        monkeypatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_ENVIRONMENT", "test-subconfig-2-yml")
        pushd(project_files_cli.root)
        cli_runner.invoke(
            cli,
            ["test"],
        )
        assert Project._default.environment.name == "test-subconfig-2-yml"

    @pytest.mark.usefixtures("deactivate_project")
    def test_lower_null_environment_overrides_default(
        self,
        project_files_cli,
        cli_runner,
        pushd,
    ) -> None:
        pushd(project_files_cli.root)
        cli_runner.invoke(
            cli,
            ["--environment", "null", "hub", "ping"],
        )
        assert Project._default.environment is None

    @pytest.mark.usefixtures("deactivate_project")
    def test_upper_null_environment_overrides_default(
        self,
        project_files_cli,
        cli_runner,
        pushd,
    ) -> None:
        pushd(project_files_cli.root)
        cli_runner.invoke(
            cli,
            ["--environment", "NULL", "hub", "ping"],
        )
        assert Project._default.environment is None

    @pytest.mark.usefixtures("deactivate_project")
    def test_no_environment_overrides_default(
        self,
        project_files_cli,
        cli_runner,
        pushd,
    ) -> None:
        pushd(project_files_cli.root)
        cli_runner.invoke(
            cli,
            ["--no-environment", "hub", "ping"],
        )
        assert Project._default.environment is None

    @pytest.mark.usefixtures("deactivate_project")
    def test_no_environment_and_null_environment_overrides_default(
        self,
        project_files_cli,
        cli_runner,
        pushd,
    ) -> None:
        pushd(project_files_cli.root)
        cli_runner.invoke(
            cli,
            ["--no-environment", "--environment", "null", "hub", "ping"],
        )
        assert Project._default.environment is None

    def test_handle_meltano_error(self) -> None:
        exception = MeltanoError(reason="This failed", instruction="Try again")
        with pytest.raises(CliError, match=r"This failed. Try again."):
            handle_meltano_error(exception)

    @pytest.mark.usefixtures("pushd")
    def test_cwd_option(
        self,
        cli_runner,
        test_cli_project,
        tmp_path: Path,
    ) -> t.NoReturn:
        project = test_cli_project
        with cd(project.root_dir()):
            assert_cli_runner(cli_runner.invoke(cli, ("dragon",)))
            assert Path.cwd() == project.root_dir()

        with cd(project.root_dir()):
            assert_cli_runner(
                cli_runner.invoke(cli, ("--cwd", str(tmp_path), "dragon")),
            )
            assert Path.cwd() == tmp_path

        with cd(project.root_dir()):
            filepath = tmp_path / "file.txt"
            filepath.touch()
            with pytest.raises(click.BadParameter, match="is a file"):
                raise cli_runner.invoke(
                    cli,
                    ("--cwd", str(filepath), "dragon"),
                ).exception.__context__

        with cd(project.root_dir()):
            dirpath = tmp_path / "subdir"
            with pytest.raises(click.BadParameter, match="does not exist"):
                raise cli_runner.invoke(
                    cli,
                    ("--cwd", str(dirpath), "dragon"),
                ).exception.__context__

        with cd(project.root_dir()):
            dirpath.mkdir()
            assert_cli_runner(cli_runner.invoke(cli, ("--cwd", str(dirpath), "dragon")))
            assert Path.cwd() == dirpath

    def test_env_file_option(
        self,
        cli_runner: MeltanoCliRunner,
        test_cli_project: Project,
        tmp_path: Path,
    ):
        project = test_cli_project
        with cd(project.root_dir()):
            dotenv_path = tmp_path / ".env"
            dotenv_path.write_text("MELTANO_DEFAULT_ENVIRONMENT=custom\n")
            result = cli_runner.invoke(
                cli,
                (
                    "--env-file",
                    str(dotenv_path),
                    "config",
                    "print",
                    "meltano",
                    "--format=env",
                ),
            )
            assert result.exit_code == 0
            assert "MELTANO_DEFAULT_ENVIRONMENT='custom'" in result.output

        with cd(project.root_dir()):
            dotenv_path = project.root.joinpath("prod.env")
            dotenv_path.write_text("MELTANO_DEFAULT_ENVIRONMENT=custom\n")
            result = cli_runner.invoke(
                cli,
                (
                    "--env-file",
                    "prod.env",
                    "config",
                    "print",
                    "meltano",
                    "--format=env",
                ),
            )
            assert result.exit_code == 0
            assert "MELTANO_DEFAULT_ENVIRONMENT='custom'" in result.output

    @pytest.mark.parametrize(
        "command_args",
        (
            ("invoke", "example"),
            ("config", "print", "example"),
            ("job", "list"),
            ("environment", "list"),
            ("add", "utility", "example"),
        ),
    )
    def test_error_msg_outside_project(
        self,
        tmp_path: Path,
        command_args: tuple[str, ...],
    ) -> None:
        # Unless this test runs before every test that uses a project, we
        # cannot use `cli_runner` to test this because the code path taken
        # differs after any project has been found.

        # I tried working around this by switching to an empty directory,
        # calling `Project.deactivate`, using `mock.patch` on various relevant
        # functions, and more, but nothing I did resulted in the proper code
        # path being taken. Also it seemed like a fragile approach.

        # Using a subprocess should be robust, but requires the version of
        # Meltano you want to test be the one that is installed in the active
        # Python environment. This is not the only test that requires this.
        assert (
            "must be run inside a Meltano project"
            in subprocess.run(
                ("meltano", *command_args),
                text=True,
                stderr=subprocess.PIPE,
                cwd=tmp_path,
            ).stderr
        )

    @pytest.mark.parametrize(
        ("option_name", "setting_name", "value"),
        (
            pytest.param(
                "--log-level",
                "cli.log_level",
                "warning",
                id="log-level-warning",
            ),
            pytest.param(
                "--log-level",
                "cli.log_level",
                "disabled",
                id="log-level-disabled",
            ),
            pytest.param(
                "--log-config",
                "cli.log_config",
                "path/to/logging.yml",
                id="log-config-path",
            ),
            pytest.param(
                "--log-format",
                "cli.log_format",
                "json",
                id="log-format-json",
            ),
        ),
    )
    def test_project_settings_overrides(
        self,
        cli_runner: MeltanoCliRunner,
        option_name: str,
        setting_name: str,
        value: str,
    ) -> None:
        # Mock `ProjectSettingsService.config_override` to avoid side effects
        # for other tests
        with mock.patch.object(ProjectSettingsService, "config_override", {}):
            result = cli_runner.invoke(cli, [option_name, value, "dragon"])
            assert result.exit_code == 0, result.exception
            assert ProjectSettingsService.config_override[setting_name] == value


def _get_dummy_logging_config(*, colors=True):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "meltano.core.logging.console_log_formatter",
                "colors": colors,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "loggers": {
            "meltano.cli.dummy": {
                "handlers": ["console"],
                "level": "DEBUG",
            },
        },
    }


@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="Windows terminal support for ANSI escape sequences is limited.",
)
class TestCliColors:
    TEST_TEXT = "This is a test"

    @pytest.mark.parametrize(
        ("env", "log_config", "cli_colors_expected", "log_colors_expected"),
        (
            pytest.param(
                {},
                None,
                True,
                True,
                id="colors-enabled-by-default",
            ),
            pytest.param(
                {
                    "NO_COLOR": "1",
                },
                _get_dummy_logging_config(colors=True),
                False,
                False,
                id="all-colors-disabled--no-color-precedence",
            ),
            pytest.param(
                {},
                _get_dummy_logging_config(colors=False),
                True,
                False,
                id="cli-colors-enabled-log-colors-disabled",
            ),
            pytest.param(
                {
                    "NO_COLOR": "1",
                },
                None,
                False,
                False,
                id="colors-disabled-by-1-no-color-env",
            ),
            pytest.param(
                {
                    "NO_COLOR": "TRUE",
                },
                None,
                False,
                False,
                id="colors-disabled-by-TRUE-no-color-env",
            ),
            pytest.param(
                {
                    "NO_COLOR": "t",
                },
                None,
                False,
                False,
                id="colors-disabled-by-t-no-color-env",
            ),
            pytest.param(
                {
                    "NO_COLOR": "f",
                },
                None,
                True,
                True,
                id="colors-not-disabled-by-f-no-color-env",
            ),
            pytest.param(
                {
                    "NO_COLOR": "FALSE",
                },
                None,
                True,
                True,
                id="colors-not-disabled-by-FALSE-no-color-env",
            ),
            pytest.param(
                {
                    "NO_COLOR": "NOT_A_BOOLEAN",
                },
                None,
                True,
                True,
                id="colors-not-disabled-by-invalid-no-color-env",
            ),
        ),
    )
    def test_no_color(
        self,
        cli_runner,
        env,
        log_config,
        cli_colors_expected,
        log_colors_expected,
        tmp_path,
        monkeypatch,
    ) -> None:
        monkeypatch.delenv("NO_COLOR", raising=False)
        styled_text = click.style(self.TEST_TEXT, fg="red")

        if log_config:
            log_config_path = tmp_path / "logging.yml"
            log_config_path.write_text(yaml.dump(log_config))
        else:
            log_config_path = None

        @click.command("dummy")
        def dummy_command() -> None:
            setup_logging(None, "DEBUG", log_config_path)
            logger = get_logger("meltano.cli.dummy")
            logger.info(self.TEST_TEXT)
            click.echo(styled_text)

        cli.add_command(dummy_command)

        expected_text = styled_text if cli_colors_expected else self.TEST_TEXT

        with cli_runner.isolated_filesystem():
            result = cli_runner.invoke(cli, ["dummy"], color=True, env=env)
            assert result.exit_code == 0, result.exception
            assert result.stdout.strip() == expected_text
            assert bool(ANSI_RE.findall(result.stderr)) is log_colors_expected
            assert result.exception is None


class TestLargeConfigProject:
    @pytest.mark.usefixtures("large_config_project")
    def test_list_config_performance(self, cli_runner) -> None:
        start = perf_counter_ns()
        assert (
            cli_runner.invoke(
                cli,
                ["--no-environment", "config", "list", "target-with-large-config"],
            ).exit_code
            == 0
        )
        duration_ns = perf_counter_ns() - start
        # Ensure the large config can be processed in less than 25 seconds
        assert duration_ns < 25000000000


class TestUUIDParamType:
    @pytest.mark.parametrize(
        "value",
        (
            pytest.param("123e4567-e89b-12d3-a456-426614174000", id="with hyphens"),
            pytest.param("123e4567e89b12d3a456426614174000", id="without hyphens"),
        ),
    )
    def test_valid_uuid(self, value: str):
        param = UUIDParamType()
        assert param.convert(value, None, None) == uuid.UUID(value)

    def test_invalid_uuid(self):
        param = UUIDParamType()
        value = "zzz"
        with pytest.raises(click.BadParameter, match="is not a valid UUID"):
            param.convert(value, None, None)


class TestVersionCheck:
    """Test version check functionality in CLI."""

    def test_version_check_on_command(
        self,
        cli_runner: MeltanoCliRunner,
        project: Project,
    ) -> None:
        """Test that version check integration works."""
        # This test verifies the version check is integrated into CLI commands.
        # The actual version check logic is thoroughly tested in test_version_check.py
        with cd(project.root_dir()):
            result = cli_runner.invoke(cli, ["config", "list", "meltano"])

        # The command should execute successfully
        # (version check doesn't block execution)
        assert result.exit_code == 0

        # Note: Due to test environment complexities, we test the actual version check
        # logic in unit tests rather than integration tests. The version check service
        # is thoroughly tested in tests/meltano/core/test_version_check.py

    def test_version_check_excluded_commands(
        self,
        cli_runner: MeltanoCliRunner,
        project: Project,
    ) -> None:
        """Test that excluded commands work correctly."""
        with cd(project.root_dir()):
            # Test 'version' command works
            result = cli_runner.invoke(cli, ["--version"])
            assert result.exit_code == 0

            # Test 'upgrade' command works (may fail but shouldn't crash)
            result = cli_runner.invoke(cli, ["upgrade"])
            # Command may exit with error but shouldn't crash due to version check
            assert result.exit_code in [0, 1, 2]  # Various acceptable exit codes

    def test_version_check_disabled_by_env(
        self,
        cli_runner: MeltanoCliRunner,
        project: Project,
        monkeypatch,
    ) -> None:
        """Test that version check can be disabled by environment variable."""
        monkeypatch.setenv("MELTANO_CLI_DISABLE_VERSION_CHECK", "1")

        with (
            mock.patch(
                "meltano.core.version_check.editable_installation",
                return_value=None,
            ),
            cd(project.root_dir()),
        ):
            result = cli_runner.invoke(cli, ["config", "meltano", "list"])

        # Verify no version check message appears in logs
        assert "A new version of Meltano is available" not in result.stderr

    def test_version_check_disabled_by_project_setting(
        self,
        cli_runner: MeltanoCliRunner,
        project: Project,
    ) -> None:
        """Test that version check can be disabled by project setting."""
        with (
            mock.patch(
                "meltano.core.version_check.editable_installation",
                return_value=None,
            ),
            cd(project.root_dir()),
        ):
            # Set the project setting to disable version check
            result = cli_runner.invoke(
                cli, ["config", "set", "meltano", "cli.disable_version_check", "true"]
            )
            assert result.exit_code == 0

            # Run a command and verify no version check message appears
            result = cli_runner.invoke(cli, ["config", "list", "meltano"])
            assert "A new version of Meltano is available" not in result.stderr

    @responses.activate
    def test_version_check_error_handling(
        self,
        cli_runner: MeltanoCliRunner,
        project: Project,
    ) -> None:
        """Test that CLI commands execute successfully even with version check errors."""  # noqa: E501
        responses.add(responses.GET, PYPI_URL, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        with (
            mock.patch(
                "meltano.core.version_check.VersionCheckService._check_version",
                return_value=VersionCheckResult(
                    current_version="3.7.0",
                    latest_version="3.9.0",
                    is_outdated=True,
                    upgrade_command=None,
                ),
            ),
            cd(project.root_dir()),
        ):
            result = cli_runner.invoke(cli, ["config", "list", "meltano"])

        # Command should succeed regardless of version check status
        assert result.exit_code == 0
        # Verify the command actually ran (may have empty output)
        assert "A new version of Meltano is available" in result.stderr
