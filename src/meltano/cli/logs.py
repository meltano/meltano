"""Log viewing CLI commands."""

from __future__ import annotations

import json
import typing as t

import click
import structlog
from rich.console import Console
from rich.table import Column, Table

from meltano.cli.params import pass_project
from meltano.cli.utils import (
    CliError,
    InstrumentedGroup,
    PartialInstrumentedCmd,
)
from meltano.core.db import project_engine
from meltano.core.job import State
from meltano.core.logging.job_logging_service import (
    JobLoggingService,
)
from meltano.core.tracking.contexts import CliEvent

if t.TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from meltano.core.project import Project
    from meltano.core.tracking.tracker import Tracker

logger = structlog.getLogger(__name__)


def _cli_db_session(project: Project, *, ctx: click.Context) -> Session:
    _, make_session = project_engine(project)
    session = make_session()
    ctx.with_resource(session)
    return session


@click.group(
    cls=InstrumentedGroup,
    name="logs",
    short_help="View job logs.",
)
def logs() -> None:
    """View and manage Meltano job logs."""


@logs.command(
    cls=PartialInstrumentedCmd,
    name="list",
    short_help="List recent job runs with their log information.",
)
@click.option(
    "--limit",
    "-l",
    type=int,
    default=10,
    help="Number of recent runs to show (default: 10).",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@pass_project()
@click.pass_context
def list_logs(
    ctx: click.Context,
    project: Project,
    limit: int,
    output_format: str,
) -> None:
    """List recent job runs with log information.

    Shows a table of recent runs with their metadata including job name,
    run ID, status, timing, and log availability.

    Examples:
        # Show last 10 runs
        meltano logs list

        # Show last 25 runs
        meltano logs list --limit 25

        # Output as JSON
        meltano logs list --format json
    """
    tracker: Tracker = ctx.obj["tracker"]
    session = _cli_db_session(project, ctx=ctx)
    job_logging_service = JobLoggingService(project)

    try:
        jobs = job_logging_service.get_recent_jobs(session, limit)

        if not jobs:
            click.echo("No job runs found.")
            tracker.track_command_event(CliEvent.completed)
            return

        if output_format == "json":
            runs = [
                {
                    "log_id": str(job.run_id),
                    "job_name": job.job_name,
                    "state": job.state.name,
                    "started_at": job.started_at.isoformat(),
                    "ended_at": job.ended_at.isoformat() if job.ended_at else None,
                    "duration_seconds": (
                        (job.ended_at - job.started_at).total_seconds()
                        if job.ended_at is not None
                        else None
                    ),
                    "trigger": job.trigger,
                }
                for job in jobs
            ]
            click.echo(json.dumps({"runs": runs, "total": len(runs)}, indent=2))
        else:
            table = Table(
                Column("STATUS", style="bold"),
                Column("LOG ID", style="bold", min_width=36),
                Column("JOB NAME", style="bold", max_width=50),
                Column("STARTED", style="bold"),
                Column("DURATION", style="bold"),
                Column("TRIGGER", style="bold"),
                title=f"Recent job runs (showing {len(jobs)} of last {limit})",
            )

            for job in jobs:
                # Status indicator
                match job.state:
                    case State.SUCCESS:
                        status = "✓ PASS"
                    case State.FAIL:
                        status = "✗ FAIL"
                    case State.RUNNING:
                        status = "→ RUN"
                    case _:  # pragma: no cover
                        # We filtered out any other states
                        status = f"  {job.state.name}"

                # Duration calculation
                if job.ended_at is not None:
                    duration_seconds = (job.ended_at - job.started_at).total_seconds()
                    if duration_seconds < 60:
                        duration = f"{duration_seconds:.1f}s"
                    elif duration_seconds < 3600:
                        duration = f"{duration_seconds / 60:.1f}m"
                    else:
                        duration = f"{duration_seconds / 3600:.1f}h"
                else:
                    duration = "running" if job.state == State.RUNNING else "unknown"

                # Format started time
                started = job.started_at.strftime("%Y-%m-%d %H:%M:%S")
                trigger = job.trigger or "manual"
                table.add_row(
                    status,
                    str(job.run_id),
                    job.job_name,
                    started,
                    duration,
                    trigger,
                )

            console = Console()
            console.print(table)
            click.echo("\nUse 'meltano logs show <LOG_ID>' to view a specific log.")

    except Exception as e:  # pragma: no cover
        tracker.track_command_event(CliEvent.failed)
        msg = f"Error listing logs: {e}"
        raise CliError(msg) from e

    tracker.track_command_event(CliEvent.completed)


@logs.command(
    cls=PartialInstrumentedCmd,
    name="show",
    short_help="Show log content for a specific run.",
)
@click.argument("log_id", required=True)
@click.option(
    "--tail",
    "-n",
    type=int,
    help="Show last N lines of the log.",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format for job metadata.",
)
@pass_project()
@click.pass_context
def show_log(
    ctx: click.Context,
    project: Project,
    log_id: str,
    tail: int | None,
    output_format: str,
) -> None:
    """Show log content for a specific job run.

    LOG_ID is the run ID (UUID) of the job, which you can get from 'meltano logs list'.

    Examples:
        # Show full log for a run
        meltano logs show 550e8400-e29b-41d4-a716-446655440000

        # Show last 50 lines
        meltano logs show 550e8400-e29b-41d4-a716-446655440000 --tail 50
    """
    tracker: Tracker = ctx.obj["tracker"]
    session = _cli_db_session(project, ctx=ctx)

    job_logging_service = JobLoggingService(project)

    try:
        job = job_logging_service.find_job_by_run_id(session, log_id)

        if not job:
            msg = f"No job found with log ID '{log_id}'"
            raise CliError(msg)  # noqa: TRY301

        # Display job metadata
        click.echo(job_logging_service.format_job_info(job, output_format))
        click.echo()

        # Read log content
        log_content, log_exists = job_logging_service.read_job_log(job, tail)

        if not log_exists:
            msg = (
                f"Log file not found for job run '{log_id}'. The log may have "
                "been cleaned up or the job may not have generated logs."
            )
            raise CliError(msg)  # noqa: TRY301

        # Handle tail mode
        if tail:
            lines = log_content.split("\n") if log_content else []
            click.echo(f"Last {len(lines)} lines:")
            click.echo("-" * 40)
            click.echo(log_content)
            tracker.track_command_event(CliEvent.completed)
            return

        # Check file size for full log display
        log_file_path = job_logging_service.get_job_log_path(job)
        if (
            log_file_path.stat().st_size > 2097152  # 2MB
            and not click.confirm(
                f"Log file is large ({log_file_path.stat().st_size / 1024 / 1024:.1f}MB). "  # noqa: E501
                "Do you want to display it anyway?"
            )
        ):
            click.echo(f"Log file path: {log_file_path}")
            tracker.track_command_event(CliEvent.completed)
            return

        # Show full log
        click.echo("Log content:")
        click.echo("-" * 12)
        click.echo(log_content, nl=False)
    except CliError:
        tracker.track_command_event(CliEvent.failed)
        raise
    except Exception as e:  # pragma: no cover
        tracker.track_command_event(CliEvent.failed)
        msg = f"Error reading log: {e}"
        raise CliError(msg) from e

    tracker.track_command_event(CliEvent.completed)


@logs.command(
    cls=PartialInstrumentedCmd,
    name="dir",
    short_help="Show the directory of the logs.",
)
@pass_project()
def directory(project: Project) -> None:
    """Show the directory of the logs."""
    logs_dir = project.dirs.logs(make_dirs=False)
    click.echo(logs_dir)
