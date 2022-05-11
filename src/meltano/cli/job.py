"""Job management CLI."""
import json

import click
import structlog
from click_default_group import DefaultGroup

from meltano.core.block.parser import BlockParser, validate_block_sets
from meltano.core.project import Project
from meltano.core.task_sets import TaskSets
from meltano.core.task_sets_service import (
    JobAlreadyExistsError,
    JobNotFoundError,
    TaskSetsService,
)
from meltano.core.tracking import GoogleAnalyticsTracker

from . import cli
from .params import pass_project

logger = structlog.getLogger(__name__)


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
            click.echo(f"{task_set.name}: {task_set.squashed_per_set}")
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

    task_set = TaskSets(ctx.obj["JOB_NAME"], tasks)
    _validate_tasks(project, task_set)

    try:
        task_sets_service.add_from_str(ctx.obj["JOB_NAME"], tasks)
    except JobAlreadyExistsError as serr:
        click.secho(f"Job '{serr.name}' already exists.", fg="yellow")
    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_job("tasks", ctx.obj["JOB_NAME"])


class JobTaskInvalidError(Exception):
    """Occurs when a task in a TaskSet (aka job) is invalid."""

    def __init__(self, name: str, error: str = None):
        """Initialize a JobTaskInvalidError.

        Args:
            name: Name of the TaskSet (aka job) that was invalid.
            error: Error message.
        """
        self.name = name
        if error:
            super().__init__(f"Job '{name}' has invalid task: {error}")
        else:
            super().__init__(f"Job '{name}' has invalid task.")


def _validate_tasks(project: Project, task_set: TaskSets) -> bool:
    """Validate the job's tasks by attempting to parse them into valid Blocks and using the Block's validation logic.

    Args:
        logger: Logger to use.
        project: Project to use.
        task_set: TaskSets to validate.

    Returns:
        True if the job's tasks are valid.

    Raises:
        JobTaskInvalidError: If the job's tasks are invalid.
    """
    for block_name in task_set:
        try:
            parser = BlockParser(logger, project, block_name)
            parsed_blocks = list(parser.find_blocks(0))
        except Exception as err:
            raise JobTaskInvalidError(block_name, err) from err
        if not validate_block_sets(logger, parsed_blocks):
            raise JobTaskInvalidError(block_name, "Block set validation failed.")
    return True
