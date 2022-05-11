"""Job management CLI."""
import json

import click
from click_default_group import DefaultGroup

from meltano.core.task_sets_service import (
    JobAlreadyExistsError,
    JobNotFoundError,
    TaskSetsService,
)
from meltano.core.tracking import GoogleAnalyticsTracker

from . import cli
from .params import pass_project


@cli.group(cls=DefaultGroup, default="tasks", short_help="Manage jobs.")
@click.pass_context
@click.argument("name", required=True)
@pass_project(migrate=True)
def job(project, ctx, name: str):
    """
    Manage jobs.

    Example usage:

    \b
    \tmeltano job JOB_NAME
    \tmeltano job JOB_NAME list
    \tmeltano job JOB_NAME tasks '[<run command>, ...]'

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#jobs
    """
    ctx.obj["project"] = project
    ctx.obj["task_sets_service"] = TaskSetsService(project)
    ctx.obj["JOB_NAME"] = name


@job.command(short_help="List tasks for a specific named job.")  # noqa: WPS441
@click.option("--format", type=click.Choice(["json", "text", "run"]), default="text")
@click.pass_context
def list(ctx, format):  # noqa: WPS125
    """List available jobs."""
    project = ctx.obj["project"]
    task_sets_service: TaskSetsService = ctx.obj["task_sets_service"]
    name: str = ctx.obj["JOB_NAME"]

    try:
        task_set = task_sets_service.get(name)
    except JobNotFoundError:
        click.secho(f"Job '{name}' does not exist.", fg="yellow")

    if format == "text":
        click.echo(f"{task_set.name}: {task_set.tasks}")
    elif format == "json":
        click.echo(
            json.dumps({"job_name": task_set.name, "tasks": task_set.tasks}, indent=2)
        )
    elif format == "run":
        click.echo(f"meltano run {task_set.squashed}")
    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_job("list", ctx.obj["JOB_NAME"])


def list_all_jobs(ctx, format: str):  # noqa: WPS125
    """List all available jobs."""
    project = ctx.obj["project"]
    task_sets_service: TaskSetsService = ctx.obj["task_sets_service"]

    if format == "text":
        for task_set in task_sets_service.list():
            click.echo(f"{task_set.name}: {task_set.squashed_sets}")
    elif format == "json":
        payload = []
        for task_set in task_sets_service.list():  # noqa: WPS440
            payload.append(
                {
                    "job_name": task_set.name,
                    "tasks": task_set.tasks,
                }
            )
        click.echo(json.dumps(payload, indent=2))

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_job("list")


@job.command(name="tasks", short_help="Add a new job with tasks.")
@click.argument("tasks")
@click.pass_context
def tasks(ctx, tasks: str):  # noqa: WPS442
    """Add tasks to a new job.

    Usage:
        meltano job JOB_NAME tasks '[<run command>, ...]'
    """
    project = ctx.obj["project"]
    task_sets_service: TaskSetsService = ctx.obj["task_sets_service"]

    try:
        task_sets_service.add_from_str(ctx.obj["JOB_NAME"], tasks)
    except JobAlreadyExistsError as serr:
        click.secho(f"Job '{serr.name}' already exists.", fg="yellow")
    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_job("tasks", ctx.obj["JOB_NAME"])
