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
from . import cli

EXTRACTORS = "extractors"
LOADERS = "loaders"
ALL = "all"


@cli.command()
@click.pass_context
@click.argument("project_name")
@click.option(
    "--no_usage_stats", help="Do not send anonymous usage stats.", is_flag=True
)
def init(ctx, project_name, no_usage_stats):
    if ctx.obj["project"]:
        logging.warn(f"Found meltano project at: {ctx.obj['project'].root}")
        raise click.ClickException(
            "`meltano init` cannot run inside a Meltano project."
        )

    init_service = ProjectInitService(project_name)
    try:
        project = init_service.init()
        init_service.echo_instructions()

        tracker = GoogleAnalyticsTracker(project)
        if no_usage_stats:
            tracker.update_permission_to_track(False)
        else:
            tracker.track_meltano_init(project_name=project_name)
    except ProjectInitServiceError as e:
        click.secho(f"Directory {project_name} already exists!", fg="red")
        raise click.Abort()
