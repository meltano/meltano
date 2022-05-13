"""Job management CLI."""
import json

import click
import structlog

from meltano.core.block.parser import BlockParser, validate_block_sets
from meltano.core.project import Project
from meltano.core.task_sets import TaskSets, tasks_from_str
from meltano.core.task_sets_service import (
    JobAlreadyExistsError,
    JobNotFoundError,
    TaskSetsService,
)
from meltano.core.tracking import GoogleAnalyticsTracker

from . import CliError, cli
from .params import pass_project

logger = structlog.getLogger(__name__)


def _list_single_job(
    project: Project,
    task_sets_service: TaskSetsService,
    list_format: str,
    job_name: str,
) -> None:
    """List a single job.

    Args:
        project: The project to use.
        task_sets_service: The task sets service to use.
        list_format: The format to use.
        job_name: The job name to list.
    """
    try:
        task_set = task_sets_service.get(job_name)
    except JobNotFoundError:
        click.secho(f"Job '{job_name}' does not exist.", fg="yellow")
        return

    if list_format == "text":
        click.echo(f"{task_set.name}: {task_set.tasks}")
    elif list_format == "json":
        click.echo(
            json.dumps({"job_name": task_set.name, "tasks": task_set.tasks}, indent=2)
        )
    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_job("list", job_name)


def _list_all_jobs(
    project: Project, task_sets_service: TaskSetsService, list_format: str
) -> None:
    """List all jobs.

    Args:
        project: The project to use.
        task_sets_service: The task sets service to use.
        list_format: The format to use.
    """
    if list_format == "text":
        for task_set in task_sets_service.list():
            click.echo(f"{task_set.name}: {task_set.tasks}")
    elif list_format == "json":
        click.echo(
            json.dumps(
                {
                    "jobs": [
                        {"job_name": tset.name, "tasks": tset.tasks}
                        for tset in task_sets_service.list()
                    ]
                },
                indent=2,
            )
        )
        tracker = GoogleAnalyticsTracker(project)
        tracker.track_meltano_job("list")


@cli.group(short_help="Manage jobs.")
@click.pass_context
@pass_project(migrate=True)
def job(project, ctx):
    """
    Manage jobs.

    Example usage:

    \b
    \t# This help
    \tmeltano job --help
    \t# List all jobs in JSON format
    \tmeltano job list --format json
    \t# List a named job
    \tmeltano job list <job_name>
    \b
    \t# Create a new job with a single task representing a run command
    \tmeltano job NAME tasks <run command>
    \t# Create a new job with multiple tasks each representing a run command
    \tmeltano job NAME tasks '[<run command1>, <run command2>, ...]'
    \b
    \t# Remove a named job
    \tmeltano job remove <job_name>

    \bRead more at https://docs.meltano.com/reference/command-line-interface#jobs
    """
    ctx.obj["project"] = project
    ctx.obj["task_sets_service"] = TaskSetsService(project)


@job.command(name="list", short_help="List job(s).")
@click.option(
    "--format",
    "list_format",
    type=click.Choice(["json", "text"]),
    default="text",
)
@click.argument("job_name", required=False, default=None)
@click.pass_context
def list_jobs(ctx, list_format: str, job_name: str):
    """List available jobs."""
    project = ctx.obj["project"]
    task_sets_service: TaskSetsService = ctx.obj["task_sets_service"]

    if job_name:
        _list_single_job(project, task_sets_service, list_format, job_name)
    else:
        _list_all_jobs(project, task_sets_service, list_format)


@job.command(name="add", short_help="Add a new job with tasks.")
@click.argument(
    "job_name",
    required=True,
    default=None,
)
@click.option(
    "--tasks",
    "raw_tasks",
    required=True,
    default=None,
    help="Tasks that will be run as part of this job.",
)
@click.pass_context
def add(ctx, job_name: str, raw_tasks: str):
    """Add tasks to a new job.

    Example usage:

    \b
    \t# Create a new job with a single task representing a single run command.
    \tmeltano job add NAME --tasks 'tap mapper target command:arg1'
    \b
    \t# Create a new job with multiple tasks each representing a run command.
    \t# The list of tasks is wrapped in square brackets and each sub-task is separated by a comma.
    \tmeltano job add NAME --tasks '[<run stmt1>, <run stmt2>, ...]'
    """
    project = ctx.obj["project"]
    task_sets_service: TaskSetsService = ctx.obj["task_sets_service"]

    raw_tasks = raw_tasks.strip("'\"")

    task_sets = tasks_from_str(job_name, raw_tasks)

    try:
        _validate_tasks(project, task_sets)
    except JobTaskInvalidError as err:
        raise CliError(f"Job '{task_sets.name}' invalid: {str(err)}")

    try:
        task_sets_service.add(task_sets)
    except JobAlreadyExistsError as serr:
        raise CliError(f"Job '{task_sets.name}' already exists.") from serr

    click.echo(f"Added job {task_sets.name}: {task_sets.tasks}")

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_job("tasks", job_name)


@job.command(name="remove", short_help="Remove a job.")
@click.argument("job_name", required=True)
@click.pass_context
def remove(ctx, job_name: str):  # noqa: WPS442
    """Remove a job.

    Usage:
        meltano job remove <job_name>
    """
    project = ctx.obj["project"]
    task_sets_service: TaskSetsService = ctx.obj["task_sets_service"]
    task_sets = task_sets_service.remove(job_name)
    click.echo(f"Removed job '{task_sets.name}'.")
    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_job("remove", job_name)


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
        project: Project to use.
        task_set: TaskSets to validate.

    Returns:
        True if the job's tasks are valid.

    Raises:
        JobTaskInvalidError: If the job's tasks are invalid.
    """
    blocks = task_set.squashed.split(" ")
    logger.debug(
        "validating tasks",
        job=task_set.name,
        tasks=task_set.tasks,
        squashed=task_set.squashed,
        blocks=blocks,
    )
    try:
        bparser = BlockParser(logger, project, blocks)
        parsed_blocks = list(bparser.find_blocks(0))
    except Exception as err:
        raise JobTaskInvalidError(blocks, err) from err
    if not validate_block_sets(logger, parsed_blocks):
        raise JobTaskInvalidError(blocks, "Block set validation failed.")
    return True
