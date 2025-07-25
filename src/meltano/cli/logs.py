"""Log viewing CLI commands."""

from __future__ import annotations

import json
import typing as t
from pathlib import Path

import click
import structlog

from meltano.cli.params import pass_project
from meltano.cli.utils import (
    CliError,
    InstrumentedGroup,
    PartialInstrumentedCmd,
)
from meltano.core.db import project_engine
from meltano.core.job import Job, State
from meltano.core.logging.job_logging_service import (
    JobLoggingService,
)
from meltano.core.tracking.contexts import CliEvent

if t.TYPE_CHECKING:
    from meltano.core.project import Project

logger = structlog.getLogger(__name__)


def _tail_file(file_path: Path, lines: int) -> list[str]:
    """Read the last N lines from a file.

    Args:
        file_path: Path to the file to read.
        lines: Number of lines to read from the end.

    Returns:
        List of the last N lines.
    """
    with file_path.open("rb") as f:
        # Seek to end of file
        f.seek(0, 2)
        file_length = f.tell()

        # Read file in reverse to find line breaks
        lines_found = []
        block_size = 1024
        blocks = []

        while len(lines_found) < lines and file_length > 0:
            # Calculate how much to read
            if file_length < block_size:
                block_size = file_length

            # Read block
            f.seek(file_length - block_size)
            blocks.append(f.read(block_size))

            # Count lines in this block
            all_content = b"".join(reversed(blocks))
            lines_found = all_content.split(b"\n")

            # Remove empty line at end if file ends with newline
            if lines_found and not lines_found[-1]:
                lines_found = lines_found[:-1]

            file_length -= block_size

        # Return the last N lines, ensuring we get exactly N lines (or fewer if file is shorter)
        result_lines = lines_found[-lines:] if lines_found else []
        return [line.decode("utf-8", errors="replace") for line in result_lines]


def _format_job_info(job: Job, format_type: str = "text") -> str:
    """Format job information for display.

    Args:
        job: The job to format.
        format_type: Output format type ('text' or 'json').

    Returns:
        Formatted job information.
    """
    if format_type == "json":
        return json.dumps(
            {
                "job_name": job.job_name,
                "run_id": str(job.run_id),
                "state": job.state.name,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "ended_at": job.ended_at.isoformat() if job.ended_at else None,
                "trigger": job.trigger,
            },
            indent=2,
        )
    return (
        f"Job: {job.job_name}\n"
        f"Run ID: {job.run_id}\n"
        f"State: {job.state.name}\n"
        f"Started: {job.started_at}\n"
        f"Ended: {job.ended_at or 'Running'}\n"
        f"Trigger: {job.trigger or 'Manual'}"
    )


@click.group(
    cls=InstrumentedGroup,
    name="logs",
    short_help="View job logs.",
)
@click.pass_context
def logs(ctx: click.Context) -> None:
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
    tracker = ctx.obj["tracker"]

    try:
        _, make_session = project_engine(project)
        with make_session() as session:
            # Get all recent jobs across all state IDs
            # Exclude STATE_EDIT operations by filtering the underlying _state field
            jobs = (
                session.query(Job)
                .filter(
                    Job._state.in_(
                        [State.SUCCESS.name, State.FAIL.name, State.RUNNING.name]
                    )
                )
                .order_by(Job.started_at.desc())
                .limit(limit)
                .all()
            )

            if not jobs:
                click.echo("No job runs found.")
                tracker.track_command_event(CliEvent.completed)
                return

            if output_format == "json":
                runs = []
                for job in jobs:
                    runs.append(
                        {
                            "log_id": str(job.run_id),
                            "job_name": job.job_name,
                            "state": job.state.name,
                            "started_at": job.started_at.isoformat()
                            if job.started_at
                            else None,
                            "ended_at": job.ended_at.isoformat()
                            if job.ended_at
                            else None,
                            "duration_seconds": (
                                (job.ended_at - job.started_at).total_seconds()
                                if job.ended_at and job.started_at
                                else None
                            ),
                            "trigger": job.trigger,
                        }
                    )
                click.echo(json.dumps({"runs": runs, "total": len(runs)}, indent=2))
            else:
                # Text table format
                click.echo(f"Recent job runs (showing {len(jobs)} of last {limit}):\n")

                # Header
                header = f"{'STATUS':<8} {'LOG ID':<36} {'JOB NAME':<30} {'STARTED':<20} {'DURATION':<10}"
                click.echo(header)
                click.echo("-" * len(header))

                for job in jobs:
                    # Status indicator
                    if job.state == State.SUCCESS:
                        status = "✓ PASS"
                    elif job.state == State.FAIL:
                        status = "✗ FAIL"
                    elif job.state == State.RUNNING:
                        status = "→ RUN"
                    else:
                        status = f"  {job.state.name}"

                    # Duration calculation
                    if job.ended_at and job.started_at:
                        duration_seconds = (
                            job.ended_at - job.started_at
                        ).total_seconds()
                        if duration_seconds < 60:
                            duration = f"{duration_seconds:.1f}s"
                        elif duration_seconds < 3600:
                            duration = f"{duration_seconds / 60:.1f}m"
                        else:
                            duration = f"{duration_seconds / 3600:.1f}h"
                    else:
                        duration = (
                            "running" if job.state == State.RUNNING else "unknown"
                        )

                    # Truncate job name if too long
                    job_display = (
                        job.job_name[:27] + "..."
                        if len(job.job_name) > 30
                        else job.job_name
                    )

                    # Format started time
                    started = (
                        job.started_at.strftime("%Y-%m-%d %H:%M:%S")
                        if job.started_at
                        else "unknown"
                    )

                    click.echo(
                        f"{status:<8} {job.run_id!s:<36} {job_display:<30} {started:<20} {duration:<10}"
                    )

                click.echo("\nUse 'meltano logs show <LOG_ID>' to view a specific log.")

    except Exception as e:
        tracker.track_command_event(CliEvent.failed)
        raise CliError(f"Error listing logs: {e}") from e

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
    tracker = ctx.obj["tracker"]

    try:
        _, make_session = project_engine(project)
        with make_session() as session:
            # Find the job by run_id across all state IDs
            job = session.query(Job).filter(Job.run_id == log_id).first()

            if not job:
                raise CliError(f"No job found with log ID '{log_id}'")

            # Display job metadata
            click.echo(_format_job_info(job, output_format))
            click.echo()

            # Find log file
            job_logging_service = JobLoggingService(project)
            log_file_path = job_logging_service.generate_log_name(
                job.job_name, str(job.run_id)
            )

            if not log_file_path.exists():
                raise CliError(
                    f"Log file not found for job run '{log_id}'. The log may have been cleaned up or the job may not have generated logs."
                )

            # Handle tail mode
            if tail:
                lines = _tail_file(log_file_path, tail)
                click.echo(f"Last {len(lines)} lines:")
                click.echo("-" * 40)
                for line in lines:
                    click.echo(line)
                tracker.track_command_event(CliEvent.completed)
                return

            # Show full log
            if log_file_path.stat().st_size > 2097152:  # 2MB
                if not click.confirm(
                    f"Log file is large ({log_file_path.stat().st_size / 1024 / 1024:.1f}MB). "
                    "Do you want to display it anyway?"
                ):
                    click.echo(f"Log file path: {log_file_path}")
                    tracker.track_command_event(CliEvent.completed)
                    return

            click.echo("Log content:")
            click.echo("-" * 40)
            with log_file_path.open("r") as f:
                for line in f:
                    click.echo(line, nl=False)

    except CliError:
        tracker.track_command_event(CliEvent.failed)
        raise
    except Exception as e:
        tracker.track_command_event(CliEvent.failed)
        raise CliError(f"Error reading log: {e}") from e

    tracker.track_command_event(CliEvent.completed)
