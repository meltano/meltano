import os
import yaml
import click
from urllib.parse import urlparse
from . import cli

EXTRACTORS = "extractors"
LOADERS = "loaders"
ALL = "all"

initialize_file = os.path.join(os.path.dirname(__file__), "initialize.yml")


@cli.command()
@click.argument("project_name")
def initialize(project_name):
    project = project_name.lower()
    with open(initialize_file) as f:
        data = yaml.load(f)
        try:
            os.mkdir(project)
        except Exception as e:
            raise e
        created_output(project, "", True)
        for key in data.keys():
            if key.startswith("/"):
                current_dir = key[1:]
                os.mkdir(os.path.join(".", project, current_dir))
                created_output(project, current_dir, False, True)
            else:
                with open(join_with_project_base(project, key), "w") as f:
                    f.write(data.get(key))
                    created_output(project, key, False, True)
    click.secho(f"🚀\t{project}", fg="green", nl=False)
    click.echo(" has been created. Next steps:")
    click.secho("1.\tRun", nl=False)
    click.secho(" pip install", fg="green")
    click.echo("2.\tRead the Meltano README.")
    click.secho("\thttps://gitlab.com/meltano/meltano/blob/master/README.md", fg="red")
    click.echo("3.\tEdit the meltano.yml file.")


def created_output(project, filename="", star=False, check=False):
    star = "⭐" if star else ""
    check = "✅" if check else ""
    click.secho(f"{star}{check}\tCreated", fg="blue", nl=False)
    click.echo(f" ./{project}/{filename}")


def join_with_project_base(project, filename):
    return os.path.join(".", project, filename)
