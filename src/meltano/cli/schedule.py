import datetime
import json
import logging
import os
import sys
from pathlib import Path

import click
from click_default_group import DefaultGroup
from meltano.core.db import project_engine
from meltano.core.job.stale_job_failer import StaleJobFailer
from meltano.core.project import Project, ProjectNotFound
from meltano.core.schedule_service import ScheduleAlreadyExistsError, ScheduleService
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.utils import coerce_datetime

from . import cli
from .params import pass_project


@cli.group(cls=DefaultGroup, default="add")
@click.pass_context
@pass_project(migrate=True)
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
    finally:
        session.close()


@schedule.command()
@click.option("--format", type=click.Choice(["json", "text"]), default="text")
@click.pass_context
def list(ctx, format):
    project = ctx.obj["project"]
    schedule_service = ctx.obj["schedule_service"]

    _, Session = project_engine(project)
    session = Session()
    try:
        StaleJobFailer().fail_stale_jobs(session)

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
            schedules = []
            for schedule in schedule_service.schedules():
                start_date = coerce_datetime(schedule.start_date)
                if start_date:
                    start_date = start_date.date().isoformat()

                last_successful_run = schedule.last_successful_run(session)
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
                        "cron_interval": schedule.cron_interval,
                        "last_successful_run_ended_at": last_successful_run_ended_at,
                        "elt_args": schedule.elt_args,
                    }
                )

            print(json.dumps(schedules, indent=2))
    finally:
        session.close()


@schedule.command(
    context_settings=dict(ignore_unknown_options=True, allow_interspersed_args=False)
)
@click.argument("name")
@click.argument("elt_options", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run(ctx, name, elt_options):
    schedule_service = ctx.obj["schedule_service"]

    schedule = schedule_service.find_schedule(name)
    process = schedule_service.run(schedule, *elt_options)

    exitcode = process.returncode
    if exitcode:
        sys.exit(exitcode)
