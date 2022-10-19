"""New Project Initialization CLI."""
from __future__ import annotations

import logging
from pathlib import Path

import click

from meltano.core.project_init_service import ProjectInitService
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.tracking import CliContext, CliEvent, Tracker

from . import cli
from .params import database_uri_option
from .utils import CliError, InstrumentedCmd

EXTRACTORS = "extractors"
LOADERS = "loaders"
ALL = "all"

logger = logging.getLogger(__name__)
path_type = click.Path(file_okay=False, path_type=Path)


@cli.command(cls=InstrumentedCmd, short_help="Create a new Meltano project.")
@click.pass_context
@click.argument("project_directory", required=False, type=path_type)
@click.option(
    "--no_usage_stats", help="Do not send anonymous usage stats.", is_flag=True
)
@database_uri_option
def init(ctx, project_directory: Path, no_usage_stats):
    """
    Create a new Meltano project.

    Read more at https://docs.meltano.com/reference/command-line-interface#init

    """
    if not project_directory:
        click.echo("We need a project name to get started!")
        project_directory = click.prompt(
            "Enter a name now to create a Meltano project", type=path_type
        )

    if ctx.obj["project"]:
        root = ctx.obj["project"].root
        logging.warning(f"Found meltano project at: {root}")
        raise CliError("`meltano init` cannot run inside a Meltano project.")

    if no_usage_stats:
        ProjectSettingsService.config_override["send_anonymous_usage_stats"] = False

    init_service = ProjectInitService(project_directory)

    project = init_service.init()
    init_service.echo_instructions(project)

    # since the project didn't exist, tracking was not initialized in cli.py
    # but now that we've created a project we can set up telemetry and fire events.
    tracker = Tracker(project)
    tracker.add_contexts(CliContext.from_click_context(ctx))
    tracker.track_command_event(CliEvent.started)
    ctx.obj["tracker"] = tracker
