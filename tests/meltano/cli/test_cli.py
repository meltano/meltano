from __future__ import annotations

import platform
import re
import shutil
from pathlib import Path
from time import perf_counter_ns

import click
import pytest
import yaml
from structlog.stdlib import get_logger

import meltano
from asserts import assert_cli_runner
from fixtures.utils import cd
from meltano.cli import cli, handle_meltano_error
from meltano.cli.utils import CliError
from meltano.core.error import EmptyMeltanoFileException, MeltanoError
from meltano.core.logging.utils import setup_logging
from meltano.core.project import PROJECT_READONLY_ENV, Project
from meltano.core.project_settings_service import ProjectSettingsService

ANSI_RE = re.compile(r"\033\[[;?0-9]*[a-zA-Z]")


class TestCli:
    @pytest.fixture()
    def project(self, test_dir, project_init_service):
        """Return the non-activated project."""
        project = project_init_service.init(  # noqa: DAR301
            activate=False, add_discovery=True
        )

        try:
            yield project
        finally:
            Project.deactivate()
            shutil.rmtree(project.root)

    @pytest.fixture()
    def deactivate_project(self):
        Project.deactivate()

    @pytest.fixture()
    def empty_project(self, empty_meltano_yml_dir, pushd):
        project = Project(empty_meltano_yml_dir)
        try:
            yield project
        finally:
            Project.deactivate()

    @pytest.mark.order(0)
    def test_activate_project(self, project, cli_runner, pushd):
        assert Project._default is None

        pushd(project.root)
        cli_runner.invoke(cli, ["discover"])

        assert Project._default is not None
        assert Project._default.root == project.root
        assert Project._default.readonly is False

    @pytest.mark.order(1)
    def test_empty_meltano_yml_project(self, empty_project, cli_runner, pushd):
        pushd(empty_project.root)
        with pytest.raises(EmptyMeltanoFileException):
            cli_runner.invoke(cli, ["config"], catch_exceptions=False)

    @pytest.mark.order(2)
    def test_activate_project_readonly_env(
        self, project, cli_runner, pushd, monkeypatch
    ):
        monkeypatch.setenv(PROJECT_READONLY_ENV, "true")

        assert Project._default is None

        pushd(project.root)
        cli_runner.invoke(cli, ["discover"])

        assert Project._default.readonly

    @pytest.mark.order(2)
    def test_activate_project_readonly_dotenv(
        self, project, cli_runner, pushd, monkeypatch
    ):
        ProjectSettingsService(project).set("project_readonly", True)

        assert Project._default is None

        pushd(project.root)
        cli_runner.invoke(cli, ["discover"])

        assert Project._default.readonly

    def test_version(self, cli_runner):
        cli_version = cli_runner.invoke(cli, ["--version"])

        assert cli_version.output == f"meltano, version {meltano.__version__}\n"

    def test_default_environment_is_activated(
        self, deactivate_project, project_files_cli, cli_runner, pushd
    ):

        pushd(project_files_cli.root)
        cli_runner.invoke(
            cli,
            ["test"],
        )
        assert Project._default.active_environment.name == "test-meltano-environment"

    def test_environment_flag_overrides_default(
        self, deactivate_project, project_files_cli, cli_runner, pushd
    ):
        pushd(project_files_cli.root)
        cli_runner.invoke(
            cli,
            ["--environment", "test-subconfig-2-yml", "test"],
        )

        assert Project._default.active_environment.name == "test-subconfig-2-yml"

    def test_environment_variable_overrides_default(
        self, deactivate_project, project_files_cli, cli_runner, pushd, monkeypatch
    ):

        monkeypatch.setenv("MELTANO_ENVIRONMENT", "test-subconfig-2-yml")
        pushd(project_files_cli.root)
        cli_runner.invoke(
            cli,
            ["test"],
        )
        assert Project._default.active_environment.name == "test-subconfig-2-yml"

    def test_lower_null_environment_overrides_default(
        self, deactivate_project, project_files_cli, cli_runner, pushd
    ):
        pushd(project_files_cli.root)
        cli_runner.invoke(
            cli,
            ["--environment", "null", "discover"],
        )
        assert Project._default.active_environment is None

    def test_upper_null_environment_overrides_default(
        self, deactivate_project, project_files_cli, cli_runner, pushd
    ):
        pushd(project_files_cli.root)
        cli_runner.invoke(
            cli,
            ["--environment", "NULL", "discover"],
        )
        assert Project._default.active_environment is None

    def test_no_environment_overrides_default(
        self, deactivate_project, project_files_cli, cli_runner, pushd
    ):
        pushd(project_files_cli.root)
        cli_runner.invoke(
            cli,
            ["--no-environment", "discover"],
        )
        assert Project._default.active_environment is None

    def test_no_environment_and_null_environment_overrides_default(  # noqa: WPS118
        self, deactivate_project, project_files_cli, cli_runner, pushd
    ):
        pushd(project_files_cli.root)
        cli_runner.invoke(
            cli,
            ["--no-environment", "--environment", "null", "discover"],
        )
        assert Project._default.active_environment is None

    def test_handle_meltano_error(self):
        exception = MeltanoError(reason="This failed", instruction="Try again")
        with pytest.raises(CliError, match="This failed. Try again."):
            handle_meltano_error(exception)

    def test_cwd_option(self, cli_runner, project, tmp_path: Path, pushd):
        with cd(project.root_dir()):
            assert_cli_runner(cli_runner.invoke(cli, ("dragon",)))
            assert Path().resolve() == project.root_dir()

        with cd(project.root_dir()):
            assert_cli_runner(
                cli_runner.invoke(cli, ("--cwd", str(tmp_path), "dragon"))
            )
            assert Path().resolve() == tmp_path

        with cd(project.root_dir()):
            filepath = tmp_path / "file.txt"
            filepath.touch()
            with pytest.raises(click.BadParameter, match="is a file"):
                raise cli_runner.invoke(
                    cli, ("--cwd", str(filepath), "dragon")
                ).exception.__context__

        with cd(project.root_dir()):
            dirpath = tmp_path / "subdir"
            with pytest.raises(click.BadParameter, match="does not exist"):
                raise cli_runner.invoke(
                    cli, ("--cwd", str(dirpath), "dragon")
                ).exception.__context__

        with cd(project.root_dir()):
            dirpath.mkdir()
            assert_cli_runner(cli_runner.invoke(cli, ("--cwd", str(dirpath), "dragon")))
            assert Path().resolve() == dirpath


def _get_dummy_logging_config(colors=True):
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
        "env,log_config,cli_colors_expected,log_colors_expected",
        [
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
        ],
    )
    def test_no_color(
        self,
        cli_runner,
        env,
        log_config,
        cli_colors_expected,
        log_colors_expected,
        tmp_path,
    ):
        styled_text = click.style(self.TEST_TEXT, fg="red")

        if log_config:
            log_config_path = tmp_path / "logging.yml"
            log_config_path.write_text(yaml.dump(log_config))
        else:
            log_config_path = None

        @cli.command("dummy")
        @click.pass_context
        def _dummy_command(ctx):
            setup_logging(None, "DEBUG", log_config_path)
            logger = get_logger("meltano.cli.dummy")
            logger.info(self.TEST_TEXT)
            click.echo(styled_text)

        expected_text = styled_text if cli_colors_expected else self.TEST_TEXT

        with cli_runner.isolated_filesystem():
            result = cli_runner.invoke(cli, ["dummy"], color=True, env=env)
            assert result.exit_code == 0, result.exception
            assert result.output.strip() == expected_text
            assert bool(ANSI_RE.match(result.stderr)) is log_colors_expected
            assert result.exception is None


class TestLargeConfigProject:
    def test_list_config_performance(self, large_config_project: Project, cli_runner):
        start = perf_counter_ns()
        assert (
            cli_runner.invoke(
                cli, ["--no-environment", "config", "target-with-large-config", "list"]
            ).exit_code
            == 0
        )
        duration_ns = perf_counter_ns() - start
        # Ensure the large config can be processed in less than 20 seconds
        assert duration_ns < 20000000000
