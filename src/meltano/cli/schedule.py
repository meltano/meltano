import os
import logging
import click
import datetime

from . import cli
from .add import add_plugin, add_transform
from .params import project
from meltano.core.project import Project, ProjectNotFound
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.schedule_service import ScheduleService, ScheduleAlreadyExistsError
from meltano.core.db import project_engine


@cli.command()
@click.argument("name")
@click.argument("extractor")
@click.argument("loader")
@click.argument("interval")
@click.option("--transform", type=click.Choice(["skip", "only", "run"]), default="skip")
@click.option(
    "--job_id", envvar="MELTANO_JOB_ID", help="A custom string to identify the job."
)
@click.option("--start-date", type=click.DateTime(), default=None)
@project
def schedule(project, name, extractor, loader, interval, transform, job_id, start_date):
    """
    meltano schedule SCHEDULE_NAME EXTRACTOR_NAME LOADER_NAME INTERVAL

    extractor_name: Which extractor should be used in this extraction
    loader_name: Which loader should be used in this extraction
    interval: Cron-like syntax to specify the interval or scheduling
    """
    _, Session = project_engine(project)
    session = Session()

    # install_missing_plugins(project, extractor, loader, transform)
    schedule_service = ScheduleService(session, project)
    tracker = GoogleAnalyticsTracker(project)

    try:
        schedule = schedule_service.add(
            name,
            extractor,
            loader,
            transform,
            interval,
            start_date,
            MELTANO_JOB_ID=job_id or "",
        )

        tracker.track_meltano_schedule(schedule)
        click.echo(f"Scheduled '{name}' at {interval}")
    except ScheduleAlreadyExistsError as serr:
        click.secho(f"Schedule '{name}' already exists.", fg="yellow")
    except Exception as err:
        click.secho(f"Scheduling failed: {err}", fg="red", err=True)
        raise click.Abort()
    finally:
        session.close()
