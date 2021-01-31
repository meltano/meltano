import logging
import os
from urllib.parse import urlparse

import click
import yaml
from meltano.core.error import SubprocessError
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.project_init_service import ProjectInitService
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.tracking import GoogleAnalyticsTracker

from . import cli
from .params import database_uri_option
from .utils import CliError

EXTRACTORS = "extractors"
LOADERS = "loaders"
ALL = "all"

logger = logging.getLogger(__name__)


@cli.command()
@click.pass_context
@click.argument("project_name")
@click.option(
    "--no_usage_stats", help="Do not send anonymous usage stats.", is_flag=True
)
@database_uri_option
def init(ctx, project_name, no_usage_stats):
    """
    Creates a new Meltano project
    """
    if ctx.obj["project"]:
        logging.warning(f"Found meltano project at: {ctx.obj['project'].root}")
        raise CliError("`meltano init` cannot run inside a Meltano project.")

    if no_usage_stats:
        ProjectSettingsService.config_override["send_anonymous_usage_stats"] = False

    init_service = ProjectInitService(project_name)
    try:
        project = init_service.init()
        init_service.echo_instructions()

        tracker = GoogleAnalyticsTracker(project)
        tracker.track_meltano_init(project_name=project_name)
    except SubprocessError as err:
        logger.error(err.stderr)
        raise
