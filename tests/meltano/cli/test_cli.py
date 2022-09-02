from __future__ import annotations

import shutil
from time import perf_counter_ns

import pytest

import meltano
from meltano.cli import cli
from meltano.core.error import EmptyMeltanoFileException
from meltano.core.project import PROJECT_READONLY_ENV, Project
from meltano.core.project_settings_service import ProjectSettingsService


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

    def test_activate_project(self, project, cli_runner, pushd):
        assert Project._default is None

        pushd(project.root)
        cli_runner.invoke(cli, ["discover"])

        assert Project._default is not None
        assert Project._default.root == project.root
        assert Project._default.readonly is False

    def test_empty_meltano_yml_project(self, empty_project, cli_runner, pushd):
        pushd(empty_project.root)
        with pytest.raises(EmptyMeltanoFileException):
            cli_runner.invoke(cli, ["config"], catch_exceptions=False)

    def test_activate_project_readonly_env(
        self, project, cli_runner, pushd, monkeypatch
    ):
        monkeypatch.setenv(PROJECT_READONLY_ENV, "true")

        assert Project._default is None

        pushd(project.root)
        cli_runner.invoke(cli, ["discover"])

        assert Project._default.readonly

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
            ["discover"],
        )
        assert Project._default.active_environment.name == "test-meltano-environment"

    def test_environment_flag_overrides_default(
        self, deactivate_project, project_files_cli, cli_runner, pushd
    ):
        pushd(project_files_cli.root)
        cli_runner.invoke(
            cli,
            ["--environment", "test-subconfig-2-yml", "discover"],
        )

        assert Project._default.active_environment.name == "test-subconfig-2-yml"

    def test_environment_variable_overrides_default(
        self, deactivate_project, project_files_cli, cli_runner, pushd, monkeypatch
    ):

        monkeypatch.setenv("MELTANO_ENVIRONMENT", "test-subconfig-2-yml")
        pushd(project_files_cli.root)
        cli_runner.invoke(
            cli,
            ["discover"],
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
