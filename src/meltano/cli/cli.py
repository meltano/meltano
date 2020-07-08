import sys
import click
import logging
import warnings

import meltano
from meltano.core.project import Project, ProjectNotFound
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.behavior.versioned import IncompatibleVersionError
from meltano.core.logging import setup_logging, LEVELS

setup_logging()


@click.group(invoke_without_command=True, no_args_is_help=True)
@click.option("--log-level", type=click.Choice(LEVELS.keys()))
@click.option("-v", "--verbose", count=True)
@click.version_option(version=meltano.__version__, prog_name="meltano")
@click.pass_context
def cli(ctx, log_level, verbose):
    """
    Get help at https://www.meltano.com/docs/command-line-interface.html
    """
    if log_level:
        ProjectSettingsService.config_override["cli.log_level"] = log_level

    ctx.ensure_object(dict)
    ctx.obj["verbosity"] = verbose

    try:
        project = Project.find()
        setup_logging(project)

        ctx.obj["project"] = project
    except ProjectNotFound as err:
        ctx.obj["project"] = None
    except IncompatibleVersionError as err:
        click.secho(
            "This meltano project is incompatible with this version of `meltano`.",
            fg="yellow",
        )
        click.echo(
            "Visit http://meltano.com/docs/installation.html#upgrading-meltano-version for more details."
        )
        sys.exit(3)
