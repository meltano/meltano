"""Schedule management CLI."""
from __future__ import annotations

import json
import sys

import click
from click_default_group import DefaultGroup
from sqlalchemy.orm import Session

from meltano.core.db import project_engine
from meltano.core.job.stale_job_failer import StaleJobFailer
from meltano.core.legacy_tracking import LegacyTracker
from meltano.core.schedule import Schedule
from meltano.core.schedule_service import (
    ScheduleAlreadyExistsError,
    ScheduleNotFoundError,
    ScheduleService,
)
from meltano.core.task_sets import TaskSets
from meltano.core.task_sets_service import TaskSetsService
from meltano.core.tracking import CliContext, CliEvent, Tracker
from meltano.core.utils import NotFound, coerce_datetime

from . import cli
from .params import pass_project


@cli.group(cls=DefaultGroup, default="add", short_help="Manage pipeline schedules.")
@click.pass_context
@pass_project(migrate=True)
def schedule(project, ctx):
    """
    Manage pipeline schedules.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#schedule
    """
    ctx.obj["project"] = project
    ctx.obj["schedule_service"] = ScheduleService(project)
    ctx.obj["task_sets_service"] = TaskSetsService(project)
    ctx.obj["tracker"] = Tracker(project)
    ctx.obj["legacy_tracker"] = LegacyTracker(
        project, context_overrides=ctx.obj["tracker"].contexts
    )


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
    tracker = ctx.obj["tracker"]
    legacy_tracker = ctx.obj["legacy_tracker"]
    schedule_service: ScheduleService = ctx.obj["schedule_service"]

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
        tracker.track_command_event(CliEvent.completed)
    except ScheduleAlreadyExistsError:
        tracker.track_command_event(CliEvent.aborted)
        click.secho(f"Schedule '{name}' already exists.", fg="yellow")
    except Exception:
        tracker.track_command_event(CliEvent.failed)
        raise
    finally:
        session.close()


def _add_job(ctx, name: str, job: str, interval: str):
    """Add a new scheduled job."""
    project = ctx.obj["project"]
    tracker = ctx.obj["tracker"]
    legacy_tracker = ctx.obj["legacy_tracker"]

    schedule_service: ScheduleService = ctx.obj["schedule_service"]

    _, session_maker = project_engine(project)
    session = session_maker()
    try:
        added_schedule = schedule_service.add(name, job, interval)
        legacy_tracker.track_meltano_schedule("add", added_schedule)
        click.echo(
            f"Scheduled job '{added_schedule.name}' at {added_schedule.interval}"
        )
        tracker.track_command_event(CliEvent.completed)
    except ScheduleAlreadyExistsError:
        tracker.track_command_event(CliEvent.aborted)
        click.secho(f"Schedule '{name}' already exists.", fg="yellow")
    except Exception:
        tracker.track_command_event(CliEvent.failed)
        raise
    finally:
        session.close()


@schedule.command(short_help="[default] Add a new schedule.")
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
def add(
    ctx, name, job, extractor, loader, transform, interval, start_date
):  # noqa: WPS238 - too many raises
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
    tracker = ctx.obj["tracker"]
    tracker.add_contexts(
        CliContext.from_command_and_kwargs(
            "schedule",
            "add",
            job=job,
            extract=extractor,
            loader=loader,
            transform=transform,
            interval=interval,
            start_date=start_date,
        )
    )
    tracker.track_command_event(CliEvent.started)

    if job and (extractor or loader):
        tracker.track_command_event(CliEvent.aborted)
        raise click.ClickException(
            "Cannot mix --job with --extractor/--loader/--transform"
        )

    if not job:
        if not extractor:
            tracker.track_command_event(CliEvent.aborted)
            raise click.ClickException("Missing --extractor")
        if not loader:
            tracker.track_command_event(CliEvent.aborted)
            raise click.ClickException("Missing --loader")

        _add_elt(ctx, name, extractor, loader, transform, interval, start_date)
        return
    _add_job(ctx, name, job, interval)


def _format_job_list_output(entry: Schedule, job: TaskSets) -> dict:
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


def _format_elt_list_output(entry: Schedule, session: Session) -> dict:
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


@schedule.command(short_help="List available schedules.")  # noqa: WPS441
@click.option("--format", type=click.Choice(["json", "text"]), default="text")
@click.pass_context
def list(ctx, format):  # noqa: WPS125
    """List available schedules."""
    project = ctx.obj["project"]
    tracker = ctx.obj["tracker"]
    legacy_tracker = ctx.obj["legacy_tracker"]
    tracker.add_contexts(
        CliContext.from_command_and_kwargs(
            "schedule",
            "list",
            format=format,
        )
    )
    tracker.track_command_event(CliEvent.started)

    schedule_service: ScheduleService = ctx.obj["schedule_service"]
    task_sets_service: TaskSetsService = ctx.obj["task_sets_service"]

    _, sessionMaker = project_engine(project)  # noqa: N806
    session = sessionMaker()
    try:
        StaleJobFailer().fail_stale_jobs(session)

        if format == "text":
            transform_elt_markers = {
                "run": ("→", "→"),
                "only": ("×", "→"),
                "skip": ("→", "x"),
            }

            for txt_schedule in schedule_service.schedules():
                if txt_schedule.job:
                    click.echo(
                        f"[{txt_schedule.interval}] job {txt_schedule.name}: {txt_schedule.job} → {task_sets_service.get(txt_schedule.job).tasks}"
                    )
                else:
                    markers = transform_elt_markers[txt_schedule.transform]
                    click.echo(
                        f"[{txt_schedule.interval}] elt {txt_schedule.name}: {txt_schedule.extractor} {markers[0]} {txt_schedule.loader} {markers[1]} transforms"
                    )

        elif format == "json":
            job_schedules = []
            elt_schedules = []
            for json_schedule in schedule_service.schedules():
                if json_schedule.job:
                    job_schedules.append(
                        _format_job_list_output(
                            json_schedule, task_sets_service.get(json_schedule.job)
                        )
                    )
                else:
                    elt_schedules.append(
                        _format_elt_list_output(json_schedule, session)
                    )
            click.echo(
                json.dumps(
                    {"schedules": {"job": job_schedules, "elt": elt_schedules}},
                    indent=2,
                )
            )
    except Exception:
        tracker.track_command_event(CliEvent.failed)
        raise
    finally:
        session.close()
    tracker.track_command_event(CliEvent.completed)
    legacy_tracker.track_meltano_schedule("list")


@schedule.command(
    context_settings={"ignore_unknown_options": True, "allow_interspersed_args": False},
    short_help="Run a schedule.",
)
@click.argument("name")
@click.argument("elt_options", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run(ctx, name, elt_options):
    """Run a schedule."""
    tracker = ctx.obj["tracker"]
    legacy_tracker = ctx.obj["legacy_tracker"]
    tracker.add_contexts(
        CliContext.from_command_and_kwargs(
            "schedule",
            "run",
            name=name,
            elt_options=elt_options,
        )
    )
    tracker.track_command_event(CliEvent.started)

    schedule_service = ctx.obj["schedule_service"]

    try:
        this_schedule = schedule_service.find_schedule(name)
    except (ScheduleNotFoundError, NotFound):
        tracker.track_command_event(CliEvent.aborted)
        raise

    try:
        process = schedule_service.run(this_schedule, *elt_options)
    except Exception:
        tracker.track_command_event(CliEvent.failed)
        raise

    legacy_tracker.track_meltano_schedule("run", this_schedule)
    tracker.track_command_event(CliEvent.completed)

    exitcode = process.returncode
    if exitcode:
        sys.exit(exitcode)


@schedule.command(name="remove", short_help="Remove a schedule.")
@click.argument("name", required=True)
@click.pass_context
def remove(ctx, name):
    """Remove a schedule.

    Usage:
        meltano schedule remove <name>
    """
    tracker = ctx.obj["tracker"]
    legacy_tracker = ctx.obj["legacy_tracker"]
    tracker.add_contexts(
        CliContext.from_command_and_kwargs(
            "schedule",
            "remove",
            name=name,
        )
    )
    tracker.track_command_event(CliEvent.started)

    schedule_service: ScheduleService = ctx.obj["schedule_service"]

    try:
        removed_schedule = schedule_service.find_schedule(name)
    except (ScheduleNotFoundError, NotFound):
        tracker.track_command_event(CliEvent.aborted)
        raise

    try:
        schedule_service.remove(name)
    except Exception:
        tracker.track_command_event(CliEvent.failed)
        raise

    legacy_tracker.track_meltano_schedule("remove", removed_schedule)
    tracker.track_command_event(CliEvent.completed)


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


@schedule.command(name="set", short_help="Update a schedule.")
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
def set_cmd(  # noqa: WPS238 - too many raises (4)
    ctx, name, interval, job, extractor, loader, transform
):
    """Update a schedule.

    Usage:
        meltano schedule set <name> [--interval <interval>] [--job <job>] [--extractor <extractor>] [--loader <loader>] [--transform <transform>]
    """
    tracker = ctx.obj["tracker"]
    legacy_tracker = ctx.obj["legacy_tracker"]
    tracker.add_contexts(
        CliContext.from_command_and_kwargs(
            "schedule",
            "set",
            name=name,
            interval=interval,
            job=job,
            extractor=extractor,
            loader=loader,
            transform=transform,
        )
    )
    tracker.track_command_event(CliEvent.started)

    schedule_service: ScheduleService = ctx.obj["schedule_service"]

    try:
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
    except (click.ClickException, ScheduleNotFoundError, NotFound):
        tracker.track_command_event(CliEvent.aborted)
        raise

    try:
        schedule_service.update_schedule(updated)
    except Exception:
        tracker.track_command_event(CliEvent.failed)
        raise

    click.echo(f"Updated schedule '{name}'")
    legacy_tracker.track_meltano_schedule("set", updated)
    tracker.track_command_event(CliEvent.completed)
