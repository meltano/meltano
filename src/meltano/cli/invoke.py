import click
import sys
import logging
from . import cli
from .params import project
from .utils import CliError

from meltano.core.plugin import PluginType
from meltano.core.plugin_invoker import invoker_factory
from meltano.core.config_service import ConfigService
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.db import project_engine
from meltano.core.error import SubprocessError


logger = logging.getLogger(__name__)


@cli.command(context_settings=dict(ignore_unknown_options=True))
@click.option(
    "--plugin-type", type=click.Choice(PluginType.cli_arguments()), default=None
)
@click.argument("plugin_name")
@click.argument("plugin_args", nargs=-1, type=click.UNPROCESSED)
@project(migrate=True)
def invoke(project, plugin_type, plugin_name, plugin_args):
    plugin_type = PluginType.from_cli_argument(plugin_type) if plugin_type else None

    _, Session = project_engine(project)
    session = Session()
    try:
        config_service = ConfigService(project)
        plugin = config_service.find_plugin(
            plugin_name, plugin_type=plugin_type, invokable=True
        )
        service = invoker_factory(project, plugin, prepare_with_session=session)
        handle = service.invoke(*plugin_args)

        exit_code = handle.wait()

        tracker = GoogleAnalyticsTracker(project)
        tracker.track_meltano_invoke(
            plugin_name=plugin_name, plugin_args=" ".join(plugin_args)
        )

        sys.exit(exit_code)
    except SubprocessError as err:
        logger.error(err.stderr)
        raise CliError(str(err)) from err
    finally:
        session.close()
