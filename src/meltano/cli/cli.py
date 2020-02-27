import sys
import click
import logging
import warnings

# disable the psycopg2 warning
# this needs to run before `psycopg2` is imported
warnings.filterwarnings("ignore", category=UserWarning, module="psycopg2")

import meltano
from meltano.core.project import Project, ProjectNotFound
from meltano.core.behavior.versioned import IncompatibleVersionError
from meltano.core.logging import setup_logging, LEVELS


logger = logging.getLogger(__name__)


@click.group(invoke_without_command=True, no_args_is_help=True)
@click.option("--log-level", type=click.Choice(LEVELS.keys()), default="info")
@click.option("-v", "--verbose", count=True)
@click.version_option(version=meltano.__version__, prog_name="meltano")
@click.pass_context
def cli(ctx, log_level, verbose):
    """
    Get help at https://www.meltano.com/developer-tools/command-line-interface.html#command-line-interface
    """
    setup_logging(log_level=log_level)

    ctx.ensure_object(dict)
    ctx.obj["verbosity"] = verbose

    try:
        ctx.obj["project"] = Project.find()
    except ProjectNotFound as err:
        ctx.obj["project"] = None
    except IncompatibleVersionError as err:
        click.secho(
            "This meltano project is incompatible with this version of `meltano`.",
            fg="yellow",
        )
        click.echo(
            "Visit http://meltano.com/developer-tools/self-hosted-installation.html#upgrading-meltano-version for more details."
        )
        sys.exit(3)
