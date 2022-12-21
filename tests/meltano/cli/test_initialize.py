from __future__ import annotations

import pytest

from meltano.cli import cli
from meltano.core.project import Project, ProjectNotFound
from meltano.core.project_init_service import ProjectInitServiceError


class TestCliInit:
    def test_init(self, cli_runner, tmp_path_factory, pushd):  # noqa: WPS210
        new_project_root = tmp_path_factory.mktemp("new_meltano_root")
        pushd(new_project_root)

        # there are no project actually
        assert Project._default is None
        with pytest.raises(ProjectNotFound):
            Project.find()

        # create one with the CLI
        cli_runner.invoke(cli, ["init", "test_project", "--no_usage_stats"])

        pushd("test_project")

        project = Project.find()

        # Deactivate project
        Project.deactivate()

        files = (
            project.root.joinpath(file).resolve()
            for file in ("meltano.yml", "README.md", ".gitignore", "requirements.txt")
        )

        meltano_dirs = (
            project.root.joinpath(meltano_dir)
            for meltano_dir in (
                ".meltano",
                "extract",
                "load",
                "transform",
                "analyze",
                "notebook",
                "orchestrate",
            )
        )

        for file in files:
            assert file.is_file()

        for meltano_dir in meltano_dirs:
            assert meltano_dir.is_dir()

        meltano_yml = project.root_dir("meltano.yml").read_text()
        assert "send_anonymous_usage_stats: false" in meltano_yml
        assert "project_id:" in meltano_yml

    def test_init_existing_empty_directory(self, cli_runner, tmp_path_factory, pushd):
        new_project_root = tmp_path_factory.mktemp("new_meltano_root")
        pushd(new_project_root)

        # create project in empty current working directory
        result = cli_runner.invoke(cli, ["init", ".", "--no_usage_stats"])
        assert "Creating project files...\n  ./" not in result.output
        assert "cd ." not in result.output

        Project.deactivate()

        new_project_root = tmp_path_factory.mktemp("new_meltano_root")
        pushd(new_project_root)

        # create project in another empty directory
        project_dir = new_project_root.joinpath("test_project")
        project_dir.mkdir()
        assert project_dir.exists()

        result = cli_runner.invoke(cli, ["init", "test_project", "--no_usage_stats"])
        assert "Creating project files...\n  test_project/" in result.output
        assert "cd test_project" in result.output

        Project.deactivate()

    def test_init_existing_meltano_yml(self, cli_runner, tmp_path_factory, pushd):
        new_project_root = tmp_path_factory.mktemp("new_meltano_root")
        new_project_root.joinpath("meltano.yml").touch()
        new_project_root.joinpath("README.md").touch()
        pushd(new_project_root)

        # create project in non-empty current working directory
        result = cli_runner.invoke(cli, ["init", ".", "--no_usage_stats"])
        assert result.exit_code == 1
        assert isinstance(result.exception, ProjectInitServiceError)
        assert "A `meltano.yml` file already exists" in result.exception.args[0]

        # forcefully create project in non-empty current working directory
        result = cli_runner.invoke(cli, ["init", ".", "--no_usage_stats", "--force"])
        assert result.exit_code == 0
        assert "Creating project files..." in result.output
        assert "meltano.yml" in result.output
        assert "README.md (skipped)" in result.output

        Project.deactivate()
