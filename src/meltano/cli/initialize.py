"""New Project Initialization CLI."""
import logging

import click

from meltano.core.error import SubprocessError
from meltano.core.legacy_tracking import LegacyTracker
from meltano.core.project_init_service import ProjectInitService
from meltano.core.project_settings_service import ProjectSettingsService

from . import cli
from .params import database_uri_option
from .utils import CliError

EXTRACTORS = "extractors"
LOADERS = "loaders"
ALL = "all"

logger = logging.getLogger(__name__)


@cli.command(short_help="Create a new Meltano project.")
@click.pass_context
@click.argument("project_name", required=False)
@click.option(
    "--no_usage_stats", help="Do not send anonymous usage stats.", is_flag=True
)
@database_uri_option
def init(ctx, project_name, no_usage_stats):
    """
    Create a new Meltano project.

    Read more at https://docs.meltano.com/reference/command-line-interface#init

    """
    if not project_name:
        click.echo("We need a project name to get started!")
        project_name = click.prompt("Enter a name now to create a Meltano project")

    if ctx.obj["project"]:
        root = ctx.obj["project"].root
        logging.warning(f"Found meltano project at: {root}")
        raise CliError("`meltano init` cannot run inside a Meltano project.")

    if no_usage_stats:
        ProjectSettingsService.config_override["send_anonymous_usage_stats"] = False

    init_service = ProjectInitService(project_name)
    try:  # noqa: WPS229
        project = init_service.init()
        init_service.echo_instructions()
        tracker = LegacyTracker(project)
        tracker.track_meltano_init(project_name=project_name)
    except SubprocessError as err:
        logger.error(err.stderr)
        raise
