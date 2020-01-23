import os
import logging
import click
import datetime

from . import cli
from .params import project
from click_default_group import DefaultGroup
from meltano.core.project import Project, ProjectNotFound
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.schedule_service import ScheduleService, ScheduleAlreadyExistsError
from meltano.core.db import project_engine


@cli.group(cls=DefaultGroup, default="add")
@click.pass_context
@project(migrate=True)
def schedule(project, ctx):
    _, Session = project_engine(project)
    session = Session()

    ctx.obj["schedule_service"] = schedule_service = ScheduleService(project)
    ctx.obj["session"] = session


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

    schedule_service = ctx.obj["schedule_service"]
    session = ctx.obj["session"]

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


@schedule.command()
@click.pass_context
def list(ctx):
    schedule_service = ctx.obj["schedule_service"]
    transform_elt_markers = {"run": ("→", "→"), "only": ("×", "→"), "skip": ("→", "x")}

    for schedule in schedule_service.schedules():
        markers = transform_elt_markers[schedule.transform]
        click.echo(
            f"[{schedule.interval}] {schedule.name}: {schedule.extractor} {markers[0]} {schedule.loader} {markers[1]} transforms"
        )
