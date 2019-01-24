import os
import yaml
import click
import shutil
import logging
from functools import singledispatch
from typing import List, Dict
from pathlib import Path

import meltano.core.bundle as bundle
from .project import Project
from .venv_service import VenvService


class ProjectInitServiceError(Exception):
    pass


class Executor:
    def write_file(self, path: Path, content: str):
        pass

    def make_dir(self):
        pass


@singledispatch
def visit(node, executor):
    pass


@visit.register(dict)
def _(node: Dict, target_path: Path = None):
    created = []

    logging.debug(f"{target_path}")
    for name, definition in node.items():
        directory = target_path.joinpath(os.path.dirname(name))

        # always create the base directory
        os.makedirs(directory, exist_ok=True)

        # recurse for the nested definition
        created += visit(definition, target_path.joinpath(name))

    return created


@visit.register(str)
def _(node: str, target_path: Path):
    """
    Create the file using either the raw content or a bundled file.
    """
    logging.debug(f"{target_path}")
    if node.startswith("bundle://"):
        # copy from the bundle
        _, path = node.split("bundle://")
        path = bundle.find(path)

        logging.debug(f"{path} → {target_path}")
        if path.is_dir():
            shutil.copytree(path, target_path)
        else:
            shutil.copy(path, target_path)
    else:
        # write the content
        with target_path.open("w") as target:
            target.write(node)

    return [target_path]


class ProjectInitService:
    def __init__(self, project_name):
        self.initialize_file = bundle.find("initialize.yml")
        self.project_name = project_name.lower()

    def init(self) -> Project:
        default_project_yaml = yaml.load(open(self.initialize_file))
        try:
            os.mkdir(self.project_name)
        except Exception as e:
            raise ProjectInitServiceError

        new_project = Project(self.project_name)
        self.project_echo("", True)

        for path in visit(default_project_yaml, Path(self.project_name)):
            self.project_echo(filename=path, star=path.is_file(), check=path.is_dir())

        return new_project

    def project_echo(self, filename="", star=False, check=False):
        star = "⭐" if star else ""
        check = "✅" if check else ""
        click.secho(f"{star}{check}\tCreated", fg="blue", nl=False)
        click.echo(f" ./{filename}")

    def echo_instructions(self):
        click.secho(f"🚀\t{self.project_name}", fg="green", nl=False)
        click.echo(" has been created. Next steps:")
        click.echo(f"🚪\tcd ", nl=False)
        click.secho(self.project_name, fg="green")
        click.echo("Try it out:")
        click.secho("🏃\tRun", nl=False)
        click.secho(" meltano add extractor tap-carbon-intensity", fg="green")
        click.secho("🏃\tRun", nl=False)
        click.secho(" meltano add loader target-sqlite", fg="green")
        click.secho("🏃\tRun", nl=False)
        click.secho(" meltano elt tap-carbon-intensity target-sqlite", fg="green")
        click.echo("🏃\tRun SQLite to check the results:")
        click.secho("\tsqlite3 meltano.db", fg="green")
        click.secho("\t sqlite> .tables", fg="green")
        click.secho("\t sqlite> SELECT * FROM region;", fg="green")
        click.secho("\t sqlite> SELECT * FROM entry LIMIT 20;", fg="green")
        click.echo("WOW! NEATO!")
        click.echo("📖\tRead the Meltano README.", nl=False)
        click.secho(
            " https://gitlab.com/meltano/meltano/blob/master/README.md", fg="red"
        )
        click.echo("✏️\tEdit the meltano.yml file.")

    def join_with_project_base(self, filename):
        return os.path.join(".", self.project_name, filename)
