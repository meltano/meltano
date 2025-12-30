"""Schedule management CLI."""

from __future__ import annotations

import json
import sys
import typing as t

import click

from meltano.cli.params import pass_project
from meltano.cli.utils import (
    CliEnvironmentBehavior,
    InstrumentedDefaultGroup,
    PartialInstrumentedCmd,
)
from meltano.core.db import project_engine
from meltano.core.job.stale_job_failer import fail_stale_jobs
from meltano.core.schedule import (
    CRON_INTERVALS,
    ELTSchedule,
    JobSchedule,
    is_valid_cron,
)
from meltano.core.schedule_service import (
    BadCronError,
    ScheduleAlreadyExistsError,
    ScheduleService,
)
from meltano.core.task_sets_service import TaskSetsService

if t.TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from meltano.core.project import Project
    from meltano.core.task_sets import TaskSets

    TransformMode: t.TypeAlias = t.Literal["skip", "only", "run"]


@click.group(
    cls=InstrumentedDefaultGroup,
    default="add",
    short_help="Manage pipeline schedules.",
    environment_behavior=CliEnvironmentBehavior.environment_optional_ignore_default,
)
@click.pass_context
@pass_project(migrate=True)
def schedule(project: Project, ctx: click.Context) -> None:
    """Manage pipeline schedules.

    \b
    Read more at https://docs.meltano.com/reference/command-line-interface#schedule
    """  # noqa: D301
    ctx.obj["project"] = project
    ctx.obj["schedule_service"] = ScheduleService(project)
    ctx.obj["task_sets_service"] = TaskSetsService(project)


def _add_elt(
    ctx: click.Context,
    name: str,
    extractor: str,
    loader: str,
    transform: TransformMode,
    interval: str,
) -> None:
    """Add a new legacy elt schedule."""
    schedule_service: ScheduleService = ctx.obj["schedule_service"]
    try:
        added_schedule = schedule_service.add_elt(
            name,
            extractor,
            loader,
            transform,
            interval,
        )
        click.echo(
            f"Scheduled elt '{added_schedule.name}' at {added_schedule.interval}",
        )
    except ScheduleAlreadyExistsError:
        click.secho(f"Schedule '{name}' already exists.", fg="yellow")


def _add_job(ctx: click.Context, name: str, job: str, interval: str) -> None:
    """Add a new scheduled job."""
    project: Project = ctx.obj["project"]
    schedule_service: ScheduleService = ctx.obj["schedule_service"]

    _, session_maker = project_engine(project)
    session = session_maker()
    try:
        added_schedule = schedule_service.add(name, job, interval)
        click.echo(
            f"Scheduled job '{added_schedule.name}' at {added_schedule.interval}",
        )
    except ScheduleAlreadyExistsError:
        click.secho(f"Schedule '{name}' already exists.", fg="yellow")
    finally:
        session.close()


class CronParam(click.ParamType):
    """Custom type definition for cron parameter."""

    name = "cron"

    def convert(self, value: str, *_) -> str:
        """Validate and con interval."""
        if value not in CRON_INTERVALS and not is_valid_cron(value):
            raise BadCronError(value)

        return value


@schedule.command(
    cls=PartialInstrumentedCmd,
    short_help="[default] Add a new schedule.",
)
@click.argument("name")
@click.option(
    "--interval",
    required=True,
    help=(
        f"Interval of the schedule. One of {', '.join(CRON_INTERVALS)} "
        "or a cron expression."
    ),
    type=CronParam(),
)
@click.option("--job", help="The name of the job to run.")
@click.option("--extractor", required=False, help="ELT Only")
@click.option("--loader", required=False, help="ELT Only")
@click.option(
    "--transform",
    type=click.Choice(["skip", "only", "run"]),
    default="skip",
    help="ELT Only",
)
@click.pass_context
def add(
    ctx: click.Context,
    name: str,
    job: str | None,
    extractor: str | None,
    loader: str | None,
    transform: TransformMode,
    interval: str,
) -> None:
    """Add a new schedule. Schedules can be used to run Meltano jobs or ELT tasks at a specific interval.

    Example usage:

    \b
    \t# Schedule a job name "my_job" to run everyday
    \tmeltano schedule add <schedule_name> --job my_job --interval "@daily"
    \t# Schedule an ELT task to run hourly
    \tmeltano schedule add <schedule_name> --extractor <tap> --loader <target> --transform run --interval "@hourly"

    \b
    Note that the --job option and --extractor/--loader options are mutually exclusive.

    \b
    Read more at https://docs.meltano.com/reference/command-line-interface#schedule
    """  # noqa: D301, E501
    if job and (extractor or loader):
        raise click.ClickException(  # noqa: TRY003
            "Cannot mix --job with --extractor/--loader/--transform",  # noqa: EM101
        )

    if job:
        _add_job(ctx, name, job, interval)
        return

    if not extractor:
        raise click.UsageError("Missing --extractor")  # noqa: EM101, TRY003
    if not loader:
        raise click.UsageError("Missing --loader")  # noqa: EM101, TRY003

    _add_elt(ctx, name, extractor, loader, transform, interval)


def _format_job_list_output(entry: JobSchedule, job: TaskSets) -> dict:
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


def _format_elt_list_output(entry: ELTSchedule, session: Session) -> dict:
    last_successful_run = entry.last_successful_run(session)
    last_successful_run_ended_at = (
        last_successful_run.ended_at.isoformat()
        if last_successful_run and last_successful_run.ended_at
        else None
    )

    return {
        "name": entry.name,
        "extractor": entry.extractor,
        "loader": entry.loader,
        "transform": entry.transform,
        "interval": entry.interval,
        "env": entry.env,
        "cron_interval": entry.cron_interval,
        "last_successful_run_ended_at": last_successful_run_ended_at,
        "elt_args": entry.elt_args,
    }


@schedule.command(
    cls=PartialInstrumentedCmd,
    name="list",
    short_help="List available schedules.",
)
@click.option(
    "--format",
    "list_format",
    type=click.Choice(("json", "text")),
    default="text",
)
@click.pass_context
def list_schedules(ctx: click.Context, list_format: str) -> None:
    """List available schedules."""
    project = ctx.obj["project"]
    schedule_service: ScheduleService = ctx.obj["schedule_service"]
    task_sets_service: TaskSetsService = ctx.obj["task_sets_service"]

    _, sessionMaker = project_engine(project)  # noqa: N806
    session = sessionMaker()
    try:
        fail_stale_jobs(session)

        if list_format == "text":
            transform_elt_markers = {
                "run": ("→", "→"),
                "only": ("×", "→"),  # noqa: RUF001
                "skip": ("→", "x"),
            }

            for txt_schedule in schedule_service.schedules():
                if isinstance(txt_schedule, JobSchedule):
                    click.echo(
                        f"[{txt_schedule.interval}] job {txt_schedule.name}: "
                        f"{txt_schedule.job} → "
                        f"{task_sets_service.get(txt_schedule.job).tasks}",
                    )
                elif isinstance(txt_schedule, ELTSchedule):
                    markers = transform_elt_markers[txt_schedule.transform]
                    click.echo(
                        f"[{txt_schedule.interval}] elt {txt_schedule.name}: "
                        f"{txt_schedule.extractor} {markers[0]} "
                        f"{txt_schedule.loader} {markers[1]} transforms",
                    )
                else:  # pragma: no cover
                    msg = f"Invalid schedule type: {type(txt_schedule)}"
                    raise ValueError(msg)  # noqa: TRY004

        elif list_format == "json":
            job_schedules = []
            elt_schedules = []
            for json_schedule in schedule_service.schedules():
                # if json_schedule.job:
                if isinstance(json_schedule, JobSchedule):
                    job_schedules.append(
                        _format_job_list_output(
                            json_schedule,
                            task_sets_service.get(json_schedule.job),
                        ),
                    )
                elif isinstance(json_schedule, ELTSchedule):
                    elt_schedules.append(
                        _format_elt_list_output(json_schedule, session),
                    )
                else:  # pragma: no cover
                    msg = f"Invalid schedule type: {type(json_schedule)}"
                    raise ValueError(msg)  # noqa: TRY004

            click.echo(
                json.dumps(
                    {"schedules": {"job": job_schedules, "elt": elt_schedules}},
                    indent=2,
                ),
            )
    finally:
        session.close()


@schedule.command(
    cls=PartialInstrumentedCmd,
    context_settings={"ignore_unknown_options": True, "allow_interspersed_args": False},
    short_help="Run a schedule.",
)
@click.argument("name")
@click.argument("elt_options", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run(ctx: click.Context, name: str, elt_options: tuple[str]) -> None:
    """Run a schedule."""
    schedule_service: ScheduleService = ctx.obj["schedule_service"]
    process = schedule_service.run(schedule_service.find_schedule(name), *elt_options)
    if process.returncode:
        sys.exit(process.returncode)


@schedule.command(
    cls=PartialInstrumentedCmd,
    name="remove",
    short_help="Remove a schedule.",
)
@click.argument("name", required=True)
@click.pass_context
def remove(ctx: click.Context, name: str) -> None:
    """Remove a schedule.

    Usage:
        meltano schedule remove <name>
    """
    ctx.obj["schedule_service"].remove_schedule(name)


@schedule.command(
    cls=PartialInstrumentedCmd,
    name="set",
    short_help="Update a schedule.",
)
@click.argument("name", required=True)
@click.option(
    "--interval",
    help=(
        f"Update the interval of the schedule. One of {', '.join(CRON_INTERVALS)} "
        "or a cron expression."
    ),
    type=CronParam(),
)
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
def set_cmd(
    ctx: click.Context,
    name: str,
    interval: str | None,
    job: str | None,
    extractor: str | None,
    loader: str | None,
    transform: TransformMode | None,
) -> None:
    """Update a schedule.

    Usage:
        meltano schedule set <name> [--interval <interval>] [--job <job>] [--extractor <extractor>] [--loader <loader>] [--transform <transform>]
    """  # noqa: E501
    schedule_service: ScheduleService = ctx.obj["schedule_service"]
    candidate = schedule_service.find_schedule(name)
    match candidate:
        case JobSchedule():
            if extractor or loader or transform:
                msg = "Cannot mix --job with --extractor/--loader/--transform"
                raise click.ClickException(msg)
            if interval:
                candidate.interval = interval
            if job:
                candidate.job = job
        case ELTSchedule():
            if job:
                msg = "Cannot mix --job with --extractor/--loader/--transform"
                raise click.ClickException(msg)
            if interval:
                candidate.interval = interval
            if extractor:
                candidate.extractor = extractor
            if loader:
                candidate.loader = loader
            if transform:
                candidate.transform = transform
        case _:  # pragma: no cover
            msg = f"Invalid schedule type: {type(candidate)}"
            raise ValueError(msg)

    schedule_service.update_schedule(candidate)
    click.echo(f"Updated schedule '{name}'")
