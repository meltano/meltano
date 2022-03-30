"""Schedule management CLI."""

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

    _, Session = project_engine(project)  # noqa: N806
    session = Session()
    try:
        added_schedule = schedule_service.add(
            session, name, extractor, loader, transform, interval, start_date
        )

        tracker = GoogleAnalyticsTracker(schedule_service.project)
        tracker.track_meltano_schedule("add", added_schedule)
        click.echo(f"Scheduled '{added_schedule.name}' at {added_schedule.interval}")
    except ScheduleAlreadyExistsError as serr:
        click.secho(
            f"Schedule '{serr.added_schedule.name}' already exists.", fg="yellow"
        )
    finally:
        session.close()


@schedule.command(short_help="List available schedules.")  # noqa: WPS441
@click.option("--format", type=click.Choice(["json", "text"]), default="text")
@click.pass_context
def list(ctx, format):  # noqa: WPS125
    """List available schedules."""
    project = ctx.obj["project"]
    schedule_service = ctx.obj["schedule_service"]

    _, Session = project_engine(project)  # noqa: N806
    session = Session()
    try:
        StaleJobFailer().fail_stale_jobs(session)

        if format == "text":
            transform_elt_markers = {
                "run": ("→", "→"),
                "only": ("×", "→"),
                "skip": ("→", "x"),
            }

            for txt_schedule in schedule_service.schedules():
                markers = transform_elt_markers[txt_schedule.transform]
                click.echo(
                    f"[{txt_schedule.interval}] {txt_schedule.name}: {txt_schedule.extractor} {markers[0]} {txt_schedule.loader} {markers[1]} transforms"
                )
        elif format == "json":
            schedules = []
            for json_schedule in schedule_service.schedules():
                start_date = coerce_datetime(json_schedule.start_date)
                if start_date:
                    start_date = start_date.date().isoformat()

                last_successful_run = json_schedule.last_successful_run(session)
                last_successful_run_ended_at = (
                    last_successful_run.ended_at.isoformat()
                    if last_successful_run
                    else None
                )

                schedules.append(
                    {
                        "name": json_schedule.name,
                        "extractor": json_schedule.extractor,
                        "loader": json_schedule.loader,
                        "transform": json_schedule.transform,
                        "interval": json_schedule.interval,
                        "start_date": start_date,
                        "env": json_schedule.env,
                        "cron_interval": json_schedule.cron_interval,
                        "last_successful_run_ended_at": last_successful_run_ended_at,
                        "elt_args": json_schedule.elt_args,
                    }
                )

            click.echo(json.dumps(schedules, indent=2))
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

    this_schedule = schedule_service.find_schedule(name)
    process = schedule_service.run(this_schedule, *elt_options)

    tracker = GoogleAnalyticsTracker(schedule_service.project)
    tracker.track_meltano_schedule("run", this_schedule)

    exitcode = process.returncode
    if exitcode:
        sys.exit(exitcode)
