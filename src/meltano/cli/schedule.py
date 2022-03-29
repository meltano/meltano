"""Defines the CLI command `meltano schedule`."""

import json
import sys

import click
from click_default_group import DefaultGroup

from meltano.core.db import project_engine
from meltano.core.job.stale_job_failer import StaleJobFailer
from meltano.core.schedule_service import ScheduleAlreadyExistsError, ScheduleService
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.utils import coerce_datetime

from . import cli
from .params import pass_project


def _print_schedules_as_text(schedule_service):
    for schedule_obj in schedule_service.schedules():
        transform_elt_markers = {
            "run": ("→", "→"),
            "only": ("×", "→"),
            "skip": ("→", "x"),
        }
        markers = transform_elt_markers[schedule_obj.transform]
        click.echo(
            f"[{schedule_obj.interval}] {schedule_obj.name}: {schedule_obj.extractor} {markers[0]} {schedule_obj.loader} {markers[1]} transforms"
        )


def _print_schedules_as_json(schedule_service):
    schedules = []
    for schedule_obj in schedule_service.schedules():
        start_date = coerce_datetime(schedule_obj.start_date)
        if start_date:
            start_date = start_date.date().isoformat()

        last_successful_run = schedule_obj.last_successful_run(session)
        last_successful_run_ended_at = (
            last_successful_run.ended_at.isoformat() if last_successful_run else None
        )

        schedules.append(
            {
                "name": schedule_obj.name,
                "extractor": schedule_obj.extractor,
                "loader": schedule_obj.loader,
                "transform": schedule_obj.transform,
                "interval": schedule_obj.interval,
                "start_date": start_date,
                "env": schedule_obj.env,
                "cron_interval": schedule_obj.cron_interval,
                "last_successful_run_ended_at": last_successful_run_ended_at,
                "elt_args": schedule_obj.elt_args,
            }
        )

    click.echo(json.dumps(schedules, indent=2))


@cli.group(cls=DefaultGroup, default="add", short_help="Manage pipeline schedules.")
@click.pass_context
@pass_project(migrate=True)
def schedule(project, ctx):
    """
    Manage pipeline schedules.

    \b\nRead more at https://meltano.com/docs/command-line-interface.html#schedule
    """
    ctx.obj["project"] = project
    ctx.obj["schedule_service"] = ScheduleService(project)


@schedule.command(short_help="[default] Add a new schedule.")
@click.argument("name")
@click.argument("extractor")
@click.argument("loader")
@click.argument("interval")
@click.option("--transform", type=click.Choice(["skip", "only", "run"]), default="skip")
@click.option("--start-date", type=click.DateTime(), default=None)
@click.pass_context
def add(ctx, name, extractor, loader, transform, interval, start_date):
    """
    Add a new schedule.

    \b
    NAME:\tThe schedule name, must be unique
    EXTRACTOR:\tWhich extractor should be used
    LOADER:\tWhich loader should be used
    INTERVAL:\tCron-like syntax to specify the schedule interval (@daily, @hourly, etc…)
    """
    project = ctx.obj["project"]
    schedule_service = ctx.obj["schedule_service"]

    _, engine_session = project_engine(project)
    session = engine_session()
    try:
        tracker = GoogleAnalyticsTracker(schedule_service.project)
        schedule_obj = schedule_service.add(
            session, name, extractor, loader, transform, interval, start_date
        )

        tracker.track_meltano_schedule("add", schedule_obj)
        click.echo(f"Scheduled '{schedule_obj.name}' at {schedule_obj.interval}")
    except ScheduleAlreadyExistsError as serr:
        click.secho(f"Schedule '{serr.schedule.name}' already exists.", fg="yellow")
    finally:
        session.close()


@schedule.command(short_help="List available schedules.")  # noqa: WPS441
@click.option("--format", type=click.Choice(["json", "text"]), default="text")
@click.pass_context
def list(ctx, format):  # noqa: WPS125
    """List available schedules."""
    project = ctx.obj["project"]
    schedule_service = ctx.obj["schedule_service"]

    _, engine_session = project_engine(project)
    session = engine_session()
    try:
        StaleJobFailer().fail_stale_jobs(session)

        if format == "text":
            _print_schedules_as_text(schedule_service)

        elif format == "json":
            _print_schedules_as_json(schedule_service)
    finally:
        session.close()

    tracker = GoogleAnalyticsTracker(schedule_service.project)
    tracker.track_meltano_schedule("list")


@schedule.command(
    context_settings={"ignore_unknown_options": True, "allow_interspersed_args": False},
    short_help="Run a schedule.",
)
@click.argument("name")
@click.argument("elt_options", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run(ctx, name, elt_options):
    """Run a schedule."""
    schedule_service = ctx.obj["schedule_service"]

    schedule_obj = schedule_service.find_schedule(name)
    process = schedule_service.run(schedule_obj, *elt_options)

    tracker = GoogleAnalyticsTracker(schedule_service.project)
    tracker.track_meltano_schedule("run", schedule_obj)

    exitcode = process.returncode
    if exitcode:
        sys.exit(exitcode)
