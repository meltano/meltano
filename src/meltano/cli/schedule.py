import os
import sys
import logging
import click
import datetime
import json
from pathlib import Path

from . import cli
from .params import project
from click_default_group import DefaultGroup
from meltano.core.project import Project, ProjectNotFound
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.schedule_service import ScheduleService, ScheduleAlreadyExistsError
from meltano.core.db import project_engine
from meltano.core.utils import coerce_datetime
from meltano.core.job import JobFinder

CRON_INTERVALS = {
    "@once": None,
    "@hourly": "0 * * * *",
    "@daily": "0 0 * * *",
    "@weekly": "0 0 * * 0",
    "@monthly": "0 0 1 * *",
    "@yearly": "0 0 1 1 *",
}


@cli.group(cls=DefaultGroup, default="add")
@click.pass_context
@project(migrate=True)
def schedule(project, ctx):
    ctx.obj["project"] = project
    ctx.obj["schedule_service"] = schedule_service = ScheduleService(project)


@schedule.command(short_help="[default] Add a new schedule")
@click.argument("name")
@click.argument("extractor")
@click.argument("loader")
@click.argument("interval")
@click.option("--transform", type=click.Choice(["skip", "only", "run"]), default="skip")
@click.option("--start-date", type=click.DateTime(), default=None)
@click.pass_context
def add(ctx, name, extractor, loader, transform, interval, start_date):
    """
    Add a new schedule

    \b
    NAME:\tThe schedule name, must be unique
    EXTRACTOR:\tWhich extractor should be used
    LOADER:\tWhich loader should be used
    INTERVAL:\tCron-like syntax to specify the schedule interval (@daily, @hourly, etc…)
    """

    project = ctx.obj["project"]
    schedule_service = ctx.obj["schedule_service"]

    _, Session = project_engine(project)
    session = Session()
    try:
        tracker = GoogleAnalyticsTracker(schedule_service.project)
        schedule = schedule_service.add(
            session, name, extractor, loader, transform, interval, start_date
        )

        tracker.track_meltano_schedule(schedule)
        click.echo(f"Scheduled '{schedule.name}' at {schedule.interval}")
    except ScheduleAlreadyExistsError as serr:
        click.secho(f"Schedule '{serr.schedule.name}' already exists.", fg="yellow")
    except Exception as err:
        click.secho(f"Scheduling failed: {err}", fg="red", err=True)
        raise click.Abort()
    finally:
        session.close()


@schedule.command()
@click.option("--format", type=click.Choice(["json", "text"]), default="text")
@click.pass_context
def list(ctx, format):
    project = ctx.obj["project"]
    schedule_service = ctx.obj["schedule_service"]

    if format == "text":
        transform_elt_markers = {
            "run": ("→", "→"),
            "only": ("×", "→"),
            "skip": ("→", "x"),
        }

        for schedule in schedule_service.schedules():
            markers = transform_elt_markers[schedule.transform]
            click.echo(
                f"[{schedule.interval}] {schedule.name}: {schedule.extractor} {markers[0]} {schedule.loader} {markers[1]} transforms"
            )
    elif format == "json":
        _, Session = project_engine(project)
        session = Session()
        try:
            schedules = []
            for schedule in schedule_service.schedules():
                start_date = coerce_datetime(schedule.start_date)
                if start_date:
                    start_date = start_date.date().isoformat()

                cron_interval = CRON_INTERVALS.get(schedule.interval, schedule.interval)

                job_finder = JobFinder(schedule.name)
                last_successful_run = job_finder.latest_success(session)
                last_successful_run_ended_at = (
                    last_successful_run.ended_at.isoformat()
                    if last_successful_run
                    else None
                )

                schedules.append(
                    {
                        "name": schedule.name,
                        "extractor": schedule.extractor,
                        "loader": schedule.loader,
                        "transform": schedule.transform,
                        "interval": schedule.interval,
                        "start_date": start_date,
                        "env": schedule.env,
                        "cron_interval": cron_interval,
                        "last_successful_run_ended_at": last_successful_run_ended_at,
                        "elt_args": [
                            schedule.extractor,
                            schedule.loader,
                            f"--job_id={schedule.name}",
                            f"--transform={schedule.transform}",
                        ],
                    }
                )
        finally:
            session.close()

        print(json.dumps(schedules))
