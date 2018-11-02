import click
import sys
from . import cli

from meltano.core.project import Project
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.config_service import ConfigService


@cli.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("plugin_name")
@click.argument("plugin_args", nargs=-1, type=click.UNPROCESSED)
def invoke(plugin_name, plugin_args):
    project = Project.find()
    config_service = ConfigService(project)

    plugin = next(
        plugin for plugin in config_service.plugins() if plugin.name == plugin_name
    )

    service = PluginInvoker(project, plugin)
    handle = service.invoke(*plugin_args)

    try:
        exit_code = handle.wait()
        sys.exit(exit_code)
    except Exception as err:
        click.secho(f"An error occured: {err}.", fg="red")
        raise click.Abort() from err
