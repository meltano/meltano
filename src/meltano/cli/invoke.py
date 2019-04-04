import click
import sys
from . import cli
from .params import project

from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.config_service import ConfigService
from meltano.core.tracking import GoogleAnalyticsTracker


@cli.command(context_settings=dict(ignore_unknown_options=True))
@project
@click.argument("plugin_name")
@click.argument("plugin_args", nargs=-1, type=click.UNPROCESSED)
def invoke(project, plugin_name, plugin_args):
    try:
        config_service = ConfigService(project)
        plugin = config_service.get_plugin(plugin_name)

        service = PluginInvoker(project, plugin)
        handle = service.invoke(*plugin_args)

        exit_code = handle.wait()

        tracker = GoogleAnalyticsTracker(project)
        tracker.track_meltano_invoke(
            plugin_name=plugin_name, plugin_args=" ".join(plugin_args)
        )

        sys.exit(exit_code)
    except Exception as err:
        click.secho(f"An error occured: {err}.", fg="red")
        raise click.Abort() from err
