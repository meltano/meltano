"""New Project Initialization CLI."""

from __future__ import annotations

from pathlib import Path

import click
import structlog

from meltano.cli.params import database_uri_option
from meltano.cli.utils import InstrumentedCmd
from meltano.core.project_init_service import ProjectInitService
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.tracking import Tracker
from meltano.core.tracking.contexts import CliContext, CliEvent

EXTRACTORS = "extractors"
LOADERS = "loaders"
ALL = "all"

logger = structlog.stdlib.get_logger(__name__)
path_type = click.Path(file_okay=False, path_type=Path)


@click.command(cls=InstrumentedCmd, short_help="Create a new Meltano project.")
@click.pass_context
@click.argument("project_directory", required=False, type=path_type)
@click.option(
    "--no-usage-stats",
    help="Do not send anonymous usage stats.",
    is_flag=True,
)
@click.option(
    "--force",
    help="Overwrite `meltano.yml` if it exists in the project directory.",
    is_flag=True,
)
@database_uri_option
def init(
    ctx: click.Context,
    project_directory: Path | None,
    *,
    no_usage_stats: bool,
    force: bool,
) -> None:
    """Create a new Meltano project.

    \b
    Read more at https://docs.meltano.com/reference/command-line-interface#init

    """  # noqa: D301
    if not project_directory:
        click.echo("We need a project name to get started!")
        project_directory = click.prompt(
            "Enter a name now to create a Meltano project",
            type=path_type,
        )

    if ctx.obj["project"]:
        root = ctx.obj["project"].root
        logger.warning(f"Found meltano project at: {root}")  # noqa: G004

    if no_usage_stats:
        ProjectSettingsService.config_override["send_anonymous_usage_stats"] = False

    init_service = ProjectInitService(project_directory)

    project = init_service.init(force=force)
    init_service.echo_instructions(project)

    # since the project didn't exist, tracking was not initialized in cli.py
    # but now that we've created a project we can set up telemetry and fire events.
    tracker = Tracker(project)
    tracker.add_contexts(CliContext.from_click_context(ctx))
    tracker.track_command_event(CliEvent.started)
    ctx.obj["tracker"] = tracker
