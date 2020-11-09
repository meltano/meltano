import click
import sys
import logging
from . import cli
from .params import project
from .utils import CliError

from meltano.core.plugin import PluginType
from meltano.core.plugin_invoker import invoker_factory, InvokerError
from meltano.core.config_service import ConfigService
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.db import project_engine
from meltano.core.error import SubprocessError


logger = logging.getLogger(__name__)


@cli.command(
    context_settings=dict(ignore_unknown_options=True, allow_interspersed_args=False)
)
@click.option(
    "--plugin-type", type=click.Choice(PluginType.cli_arguments()), default=None
)
@click.option(
    "--dump",
    type=click.Choice(["catalog", "config"]),
    help="Dump content of generated file",
)
@click.argument("plugin_name")
@click.argument("plugin_args", nargs=-1, type=click.UNPROCESSED)
@project(migrate=True)
def invoke(project, plugin_type, dump, plugin_name, plugin_args):
    plugin_type = PluginType.from_cli_argument(plugin_type) if plugin_type else None

    _, Session = project_engine(project)
    session = Session()
    try:
        config_service = ConfigService(project)
        plugin = config_service.find_plugin(
            plugin_name, plugin_type=plugin_type, invokable=True
        )
        invoker = invoker_factory(project, plugin)
        with invoker.prepared(session):
            if dump:
                dump_file(invoker, dump)
                exit_code = 0
            else:
                handle = invoker.invoke(*plugin_args)
                exit_code = handle.wait()

        tracker = GoogleAnalyticsTracker(project)
        tracker.track_meltano_invoke(
            plugin_name=plugin_name, plugin_args=" ".join(plugin_args)
        )

        sys.exit(exit_code)
    except InvokerError as err:
        raise CliError(str(err)) from err
    except SubprocessError as err:
        logger.error(err.stderr)
        raise CliError(str(err)) from err
    finally:
        session.close()


def dump_file(invoker, file_id):
    try:
        content = invoker.dump(file_id)
        print(content)
    except FileNotFoundError as err:
        raise CliError(f"Could not find {file_id}") from err
    except Exception as err:
        raise CliError(f"Could not dump {file_id}: {err}") from err
