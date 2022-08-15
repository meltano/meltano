"""Schedule management CLI."""

from __future__ import annotations

import json
import sys
from contextlib import closing
from typing import Any, Iterable

import click
from sqlalchemy.orm import Session

from meltano.core.db import project_engine
from meltano.core.job.stale_job_failer import fail_stale_jobs
from meltano.core.legacy_tracking import LegacyTracker
from meltano.core.schedule import Schedule
from meltano.core.schedule_service import ScheduleAlreadyExistsError, ScheduleService
from meltano.core.task_sets import TaskSets
from meltano.core.task_sets_service import TaskSetsService
from meltano.core.utils import coerce_datetime

from . import cli
from .params import pass_project
from .utils import InstrumentedDefaultGroup, PartialInstrumentedCmd


@cli.group(
    cls=InstrumentedDefaultGroup,
    default="add",
    name="schedule",
    short_help="Manage pipeline schedules.",
)
@click.pass_context
@pass_project(migrate=True)
def schedule_cli(project, ctx):
    """
    Manage pipeline schedules.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#schedule
    """
    ctx.obj["project"] = project
    ctx.obj["schedule_service"] = ScheduleService(project)  # noqa: WPS204
    ctx.obj["task_sets_service"] = TaskSetsService(project)


def _add_elt(
    ctx,
    name: str,
    extractor: str,
    loader: str,
    transform: str,
    interval: str,
    start_date: str | None,
):
    """Add a new legacy elt schedule."""
    project = ctx.obj["project"]
    schedule_service: ScheduleService = ctx.obj["schedule_service"]
    legacy_tracker: LegacyTracker = ctx.obj["legacy_tracker"]

    _, session_maker = project_engine(project)
    session = session_maker()
    try:
        added_schedule = schedule_service.add_elt(
            session, name, extractor, loader, transform, interval, start_date
        )
        legacy_tracker.track_meltano_schedule("add", added_schedule)
        click.echo(
            f"Scheduled elt '{added_schedule.name}' at {added_schedule.interval}"
        )
    except ScheduleAlreadyExistsError:
        click.secho(f"Schedule '{name}' already exists.", fg="yellow")
    finally:
        session.close()


def _add_job(ctx, name: str, job: str, interval: str):
    """Add a new scheduled job."""
    project = ctx.obj["project"]
    schedule_service: ScheduleService = ctx.obj["schedule_service"]
    legacy_tracker: LegacyTracker = ctx.obj["legacy_tracker"]

    _, session_maker = project_engine(project)
    session = session_maker()
    try:
        added_schedule = schedule_service.add(name, job, interval)
        legacy_tracker.track_meltano_schedule("add", added_schedule)
        click.echo(
            f"Scheduled job '{added_schedule.name}' at {added_schedule.interval}"
        )
    except ScheduleAlreadyExistsError:
        click.secho(f"Schedule '{name}' already exists.", fg="yellow")
    finally:
        session.close()


@schedule_cli.command(
    cls=PartialInstrumentedCmd, short_help="[default] Add a new schedule."
)
@click.argument("name")
@click.option("--interval", required=True, help="Interval of the schedule.")
@click.option("--job", help="The name of the job to run.")
@click.option("--extractor", required=False, help="ELT Only")
@click.option("--loader", required=False, help="ELT Only")
@click.option(
    "--transform",
    type=click.Choice(["skip", "only", "run"]),
    default="skip",
    help="ELT Only",
)
@click.option("--start-date", type=click.DateTime(), default=None, help="ELT Only")
@click.pass_context
def add(ctx, name, job, extractor, loader, transform, interval, start_date):
    """
    Add a new schedule. Schedules can be used to run Meltano jobs or ELT tasks at a specific interval.

    Example usage:

    \b
    \t# Schedule a job name "my_job" to run everyday
    \tmeltano schedule add <schedule_name> --job my_job --interval "@daily"
    \t# Schedule an ELT task to run hourly
    \tmeltano schedule add <schedule_name> --extractor <tap> --loader <target> --transform run --interval "@hourly"

    \b\nNote that the --job option and --extractor/--loader options are mutually exclusive.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#schedule
    """
    if job and (extractor or loader):
        raise click.ClickException(
            "Cannot mix --job with --extractor/--loader/--transform"
        )

    if not job:
        if not extractor:
            raise click.ClickException("Missing --extractor")
        if not loader:
            raise click.ClickException("Missing --loader")

        _add_elt(ctx, name, extractor, loader, transform, interval, start_date)
        return
    _add_job(ctx, name, job, interval)


def _format_json_job(entry: Schedule, job: TaskSets) -> dict[str, Any]:
    return {
        "name": entry.name,
        "interval": entry.interval,
        "cron_interval": entry.cron_interval,
        "env": entry.env,
        "job": {
            "name": job.name,
            "tasks": job.tasks,
        },
    }


def _format_json_elt(entry: Schedule, session: Session) -> dict[str, Any]:
    start_date = coerce_datetime(entry.start_date)
    if start_date:
        start_date = start_date.date().isoformat()

    last_successful_run = entry.last_successful_run(session)
    last_successful_run_ended_at = (
        last_successful_run.ended_at.isoformat() if last_successful_run else None
    )

    return {
        "name": entry.name,
        "extractor": entry.extractor,
        "loader": entry.loader,
        "transform": entry.transform,
        "interval": entry.interval,
        "start_date": start_date,
        "env": entry.env,
        "cron_interval": entry.cron_interval,
        "last_successful_run_ended_at": last_successful_run_ended_at,
        "elt_args": entry.elt_args,
    }


def _format_json_schedules(ctx: click.Context) -> Iterable[str]:
    schedules = {"job": [], "elt": []}

    for schedule in ctx.obj["schedule_service"].schedules():
        schedules["job" if schedule.job else "elt"].append(schedule)

    formatted_schedules = {
        "job": [
            _format_json_job(schedule, ctx.obj["task_sets_service"].get(schedule.job))
            for schedule in schedules["job"]
        ],
        "elt": [],
    }

    # Only open a DB session if necessary.
    if schedules["elt"]:
        _, session_maker = project_engine(ctx.obj["project"])
        with closing(session_maker()) as session:
            for schedule in schedules["elt"]:
                formatted_schedules["elt"].append(_format_json_elt(schedule, session))

    # For consistency with the other `list_*_schedule` functions, we yield the
    # JSON line-by-line:
    yield from json.dumps({"schedules": formatted_schedules}, indent=2).split("\n")


def _format_cron_schedules(ctx: click.Context) -> Iterable[str]:
    project_dir = ctx.obj["project"].root.resolve()
    for schedule in ctx.obj["schedule_service"].schedules():
        interval = schedule.cron_interval if schedule.job else schedule.interval
        args = schedule.job if schedule.job else " ".join(schedule.elt_args)
        cmd = "run" if schedule.job else "elt"
        env_str = " ".join(f"{key}='{value}'" for key, value in schedule.env.items())
        yield (
            f"{interval} (cd {project_dir} && {env_str} meltano {cmd} {args}) 2>&1 | logger -t meltano"
        )


def _format_text_schedules(ctx: click.Context) -> Iterable[str]:
    task_sets_service: TaskSetsService = ctx.obj["task_sets_service"]
    transform_elt_markers = {
        "run": "→→",
        "only": "×→",
        "skip": "→x",
    }
    for schedule in ctx.obj["schedule_service"].schedules():
        if schedule.job:
            yield (
                f"[{schedule.interval}] job {schedule.name}: "
                f"{schedule.job} → {task_sets_service.get(schedule.job).tasks}"
            )
        else:
            el_marker, t_marker = transform_elt_markers[schedule.transform]
            yield (
                f"[{schedule.interval}] elt {schedule.name}: "
                f"{schedule.extractor} {el_marker} {schedule.loader} {t_marker} transforms"
            )


@schedule_cli.command(
    cls=PartialInstrumentedCmd,
    name="list",
    short_help="List available schedules.",
)
@click.option(
    "--format",
    "schedule_format",
    type=click.Choice(("text", "json", "cron")),
    default="text",
)
@click.pass_context
def list_command(ctx: click.Context, schedule_format: str) -> None:
    """List available schedules."""
    click.echo(
        "\n".join(
            {
                "text": _format_text_schedules,
                "json": _format_json_schedules,
                "cron": _format_cron_schedules,
            }[schedule_format](ctx)
        )
    )

    legacy_tracker: LegacyTracker = ctx.obj["legacy_tracker"]
    legacy_tracker.track_meltano_schedule("list")


@schedule_cli.command(
    cls=PartialInstrumentedCmd,
    context_settings={"ignore_unknown_options": True, "allow_interspersed_args": False},
    short_help="Run a schedule.",
)
@click.argument("name")
@click.argument("elt_options", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run(ctx, name, elt_options):
    """Run a schedule."""
    schedule_service = ctx.obj["schedule_service"]

    this_schedule = schedule_service.find_schedule(name)
    process = schedule_service.run(this_schedule, *elt_options)

    legacy_tracker: LegacyTracker = ctx.obj["legacy_tracker"]
    legacy_tracker.track_meltano_schedule("run", this_schedule)

    exitcode = process.returncode
    if exitcode:
        sys.exit(exitcode)


@schedule_cli.command(
    cls=PartialInstrumentedCmd, name="remove", short_help="Remove a schedule."
)
@click.argument("name", required=True)
@click.pass_context
def remove(ctx, name):
    """Remove a schedule.

    Usage:
        meltano schedule remove <name>
    """
    schedule_service: ScheduleService = ctx.obj["schedule_service"]
    removed_schedule = schedule_service.find_schedule(name)
    schedule_service.remove(name)
    legacy_tracker: LegacyTracker = ctx.obj["legacy_tracker"]
    legacy_tracker.track_meltano_schedule("remove", removed_schedule)


def _update_job_schedule(
    candidate: Schedule,
    job: str | None,
    interval: str = None,
) -> Schedule:
    """Update an existing job schedule.

    Args:
        candidate: The schedule to update.
        job: The name of the job to run.
        interval: The interval of the schedule.

    Raises:
        click.ClickException: If the schedule is not a scheduled job.

    Returns:
        The updated schedule.
    """
    if not candidate.job:
        raise click.ClickException(
            f"Cannot update schedule {candidate.name} with job only flags as its a elt schedule"
        )
    if job:
        candidate.job = job
    if interval:
        candidate.interval = interval
    return candidate


def _update_elt_schedule(
    candidate: Schedule,
    extractor: str | None,
    loader: str | None,
    transform: str | None,
    interval: str | None,
) -> Schedule:
    """Update an elt schedule.

    Args:
        candidate: The schedule to update.
        extractor: The name of the extractor to use.
        loader: The name of the loader to use.
        transform: The transform flag to use.
        interval: The interval of the schedule.

    Raises:
        click.ClickException: If the schedule is not a scheduled elt task.

    Returns:
        The updated schedule.
    """
    if candidate.job:
        raise click.ClickException(
            f"Cannot update schedule {candidate.name} with elt only flags as its a scheduled job"
        )

    if extractor:
        candidate.extractor = extractor
    if loader:
        candidate.loader = loader
    if transform:
        candidate.transform = transform
    if interval:
        candidate.interval = interval
    return candidate


@schedule_cli.command(
    cls=PartialInstrumentedCmd, name="set", short_help="Update a schedule."
)
@click.argument("name", required=True)
@click.option("--interval", help="Update the interval of the schedule.")
@click.option("--job", help="Update the name of the job to run a scheduled job.")
@click.option("--extractor", help="Update the extractor for an elt schedule.")
@click.option("--loader", help="Updated the loader for an elt schedule.")
@click.option(
    "--transform",
    type=click.Choice(["skip", "only", "run"]),
    default=None,
    help="Update the transform flag for an elt schedule.",
)
@click.pass_context
def set_cmd(ctx, name, interval, job, extractor, loader, transform):
    """Update a schedule.

    Usage:
        meltano schedule set <name> [--interval <interval>] [--job <job>] [--extractor <extractor>] [--loader <loader>] [--transform <transform>]
    """
    schedule_service: ScheduleService = ctx.obj["schedule_service"]
    candidate = schedule_service.find_schedule(name)

    if candidate.job:
        if extractor or loader or transform:
            raise click.ClickException(
                "Cannot mix --job with --extractor/--loader/--transform"
            )
        updated = _update_job_schedule(candidate, job, interval)
    else:
        if job:
            raise click.ClickException(
                "Cannot mix --job with --extractor/--loader/--transform"
            )
        updated = _update_elt_schedule(
            candidate, extractor, loader, transform, interval
        )

    schedule_service.update_schedule(updated)

    click.echo(f"Updated schedule '{name}'")
    legacy_tracker: LegacyTracker = ctx.obj["legacy_tracker"]
    legacy_tracker.track_meltano_schedule("set", updated)
