import os
import yaml
import click
import logging
from urllib.parse import urlparse

from meltano.core.project_init_service import (
    ProjectInitService,
    ProjectInitServiceError,
)
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.error import SubprocessError
from . import cli
from .params import db_options

EXTRACTORS = "extractors"
LOADERS = "loaders"
ALL = "all"


@cli.command()
@click.pass_context
@click.argument("project_name")
@click.option(
    "--no_usage_stats", help="Do not send anonymous usage stats.", is_flag=True
)
@db_options
def init(engine_uri, ctx, project_name, no_usage_stats):
    """
    Creates a new Meltano project
    """
    if ctx.obj["project"]:
        logging.warning(f"Found meltano project at: {ctx.obj['project'].root}")
        raise click.ClickException(
            "`meltano init` cannot run inside a Meltano project."
        )

    init_service = ProjectInitService(project_name)
    try:
        project = init_service.init(engine_uri=engine_uri)
        init_service.echo_instructions()

        tracker = GoogleAnalyticsTracker(project)
        if no_usage_stats:
            tracker.update_permission_to_track(False)
        else:
            tracker.track_meltano_init(project_name=project_name)
    except ProjectInitServiceError as e:
        click.secho(f"Directory {project_name} already exists!", fg="red")
        raise click.Abort()
    except SubprocessError as proc_err:
        click.secho(str(proc_err), fg="red")
        click.secho(proc_err.stderr, err=True)
        raise click.Abort()
