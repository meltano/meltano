import pytest
import os
from click.testing import CliRunner

from meltano.cli import cli
from meltano.core.project import Project, ProjectNotFound


@pytest.fixture()
def cli_runner():
    return CliRunner()


def test_init(cli_runner, tmp_path_factory, pushd):
    new_project_root = tmp_path_factory.mktemp("new_meltano_root")
    pushd(new_project_root)
    Project._default = None

    # there are no project actually
    with pytest.raises(ProjectNotFound):
        Project.find()

    # create one with the CLI
    cli_runner.invoke(cli, ["init", "test_project", "--no_usage_stats"])

    pushd("test_project")

    project = Project.find()

    files = (
        project.root.joinpath(file).resolve()
        for file in ("meltano.yml", "README.md", ".gitignore", "requirements.txt")
    )

    dirs = (
        project.root.joinpath(dir)
        for dir in (
            "model",
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

    for dir in dirs:
        assert dir.is_dir()
