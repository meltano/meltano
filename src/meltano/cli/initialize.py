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
def init(project_name):
    project = project_name.lower()
    default_project_yaml = yaml.load(open(initialize_file))
    try:
        os.mkdir(project)
    except Exception as e:
        click.secho(f"Directory {project} already exists!", fg="red")
        raise click.Abort()

    project_echo(project, "", True)
    for name in default_project_yaml.keys():
        if name.startswith("/"):
            create_dir(project, name)
        else:
            create_file(project, name, default_project_yaml[name])

    click.secho(f"🚀\t{project}", fg="green", nl=False)
    click.echo(" has been created. Next steps:")
    click.secho("1.\tRun", nl=False)
    click.secho(" pip install", fg="green")
    click.echo("2.\tRead the Meltano README.")
    click.secho("\thttps://gitlab.com/meltano/meltano/blob/master/README.md", fg="red")
    click.echo("3.\tEdit the meltano.yml file.")


def create_file(project, name, content):
    with open(join_with_project_base(project, name), "w") as f:
        f.write(content)
        project_echo(project, name, False, True)


def create_dir(project, name):
    current_dir = name[1:]
    os.mkdir(os.path.join(".", project, current_dir))
    project_echo(project, current_dir, False, True)


def project_echo(project, filename="", star=False, check=False):
    star = "⭐" if star else ""
    check = "✅" if check else ""
    click.secho(f"{star}{check}\tCreated", fg="blue", nl=False)
    click.echo(f" ./{project}/{filename}")


def join_with_project_base(project, filename):
    return os.path.join(".", project, filename)
