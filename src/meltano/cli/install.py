import click
from ..support.project_add_service import ProjectAddService

@cli.command()
@click.argument(
    "plugin_type",
    type=click.Choice([ProjectAddService.EXTRACTOR, ProjectAddService.LOADER]),
)
@click.argument("plugin_name")
def install(project_name):
    init_service = ProjectInitService(project_name)
    try:
        init_service.init()
        init_service.echo_instructions()
    except ProjectInitServiceError as e:
        print(e)
        click.secho(f"Directory {init_service.project} already exists!", fg="red")
        raise click.Abort()
