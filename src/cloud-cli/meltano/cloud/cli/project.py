"""Meltano Cloud `project` command."""

from __future__ import annotations

import asyncio
import json
import logging
import platform
import sys
import typing as t

import click
import questionary
import tabulate

from meltano.cloud.api.client import MeltanoCloudClient
from meltano.cloud.cli.base import pass_context, run_async

if t.TYPE_CHECKING:
    from meltano.cloud.api.config import MeltanoCloudConfig
    from meltano.cloud.api.types import CloudProject
    from meltano.cloud.cli.base import MeltanoCloudCLIContext

DEFAULT_GET_PROJECTS_LIMIT = 125
MAX_PAGE_SIZE = 250

logger = logging.getLogger()


class ProjectsCloudClient(MeltanoCloudClient):
    """A Meltano Cloud client with extensions for projects."""

    async def get_projects(
        self,
        *,
        project_id: str | None = None,
        project_name: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ):
        """Use GET to get Meltano Cloud project projects.

        Args:
            project_id: The Meltano Cloud ID for the project.
            project_name: The name of the project.
            page_size: The number of items to request per page.
            page_token: The page token.
        """
        async with self.authenticated():
            return await self._json_request(
                "GET",
                f"/projects/v1/{self.config.tenant_resource_key}",
                params=self.clean_params(
                    {
                        "project_id": project_id,
                        "project_name": project_name,
                        "page_size": page_size,
                        "page_token": page_token,
                    },
                ),
            )


@click.group("project")
def project_group() -> None:
    """Interact with Meltano Cloud projects."""


def _safe_get_internal_project_id(config: MeltanoCloudConfig) -> str | None:
    """Get the internal project ID, or `None` if it could not be obtained."""
    try:
        return config.internal_project_id
    except Exception:
        logger.debug(
            "Could not get internal project ID from config; using `None` instead.",
        )
        return None


async def _get_projects(
    config: MeltanoCloudConfig,
    *,
    project_id: str | None = None,
    project_name: str | None = None,
    limit: int = DEFAULT_GET_PROJECTS_LIMIT,
) -> list[CloudProject]:
    page_token = None
    page_size = min(limit, MAX_PAGE_SIZE)
    results: list[CloudProject] = []

    async with ProjectsCloudClient(config=config) as client:
        while True:
            response = await client.get_projects(
                project_id=project_id,
                project_name=project_name,
                page_size=page_size,
                page_token=page_token,
            )

            results.extend(response["results"])

            if response["pagination"] and len(results) < limit:
                page_token = response["pagination"]["next_page_token"]
            else:
                break

    return [
        {
            **x,  # type: ignore[misc]
            "default": x["project_id"] == _safe_get_internal_project_id(config),
        }
        for x in results[:limit]
    ]


def _process_table_row(project: CloudProject) -> tuple[str, ...]:
    return (
        "X" if project["default"] else "",
        project["project_name"],
        project["git_repository"],
    )


def _format_projects_table(projects: list[CloudProject], table_format: str) -> str:
    """Format the projects as a table.

    Args:
        projects: The projects to format.

    Returns:
        The formatted projects.
    """
    return tabulate.tabulate(
        [_process_table_row(project) for project in projects],
        headers=(
            "Default",
            "Name",
            "Git Repository",
        ),
        tablefmt=table_format,
        # To avoid a tabulate bug (IndexError), only set colalign if there are projects
        colalign=("center", "left", "left") if projects else (),
    )


private_project_attributes = {"tenant_resource_key", "project_id"}


def _remove_private_project_attributes(project: CloudProject) -> dict[str, t.Any]:
    return {k: v for k, v in project.items() if k not in private_project_attributes}


project_list_formatters = {
    "json": lambda x: json.dumps(x, indent=2),
    "markdown": lambda x: _format_projects_table(x, table_format="github"),
    "terminal": lambda x: _format_projects_table(x, table_format="rounded_outline"),
}


@project_group.command("list")
@click.option(
    "--limit",
    required=False,
    type=int,
    default=DEFAULT_GET_PROJECTS_LIMIT,
    help="The maximum number of projects to display.",
)
@click.option(
    "--format",
    "output_format",
    required=False,
    default="terminal",
    type=click.Choice(("terminal", "markdown", "json")),
    help="The output format to use.",
)
@pass_context
@run_async
async def list_projects(
    context: MeltanoCloudCLIContext,
    output_format: str,
    limit: int,
) -> None:
    """List Meltano Cloud projects."""
    click.echo(
        project_list_formatters[output_format](
            [
                _remove_private_project_attributes(x)
                for x in (await _get_projects(config=context.config, limit=limit))
            ],
        ),
    )


def _check_for_duplicate_project_names(projects: list[CloudProject]) -> None:
    project_names = [x["project_name"] for x in projects]
    if len(set(project_names)) != len(project_names):
        click.secho(
            "Error: Multiple Meltano Cloud projects have the same name. "
            "Please specify the project using the `--id` option with its "
            "internal ID, shown below. Note that these IDs may change at any "
            "time. To avoid this issue, please use unique project names.",
            fg="red",
        )
        for project in projects:
            click.echo(
                f"{project['project_id']}: {project['project_name']} "
                f"({project['git_repository']!r})",
            )
        sys.exit(1)


class ProjectChoicesQuestionaryOption(click.Option):
    """Click option that provides an interactive prompt for Cloud Project names."""

    def prompt_for_value(self, ctx: click.Context) -> t.Any:
        """Prompt the user to interactively select a Meltano Cloud project by name.

        Args:
            ctx: The Click context.

        Returns:
            The name of the selected project, or `None` if the project was
            selected using the `--id` option.
        """
        if "project_id" in ctx.params:
            # The project has been specified by ID - don't prompt for a name
            return None

        if platform.system() == "Windows":
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy(),  # type: ignore[attr-defined]
            )

        context: MeltanoCloudCLIContext = ctx.obj
        context.projects = asyncio.run(_get_projects(context.config))
        _check_for_duplicate_project_names(context.projects)
        default_project_name = next(
            (
                x
                for x in context.projects
                if x["project_id"] == context.config.default_project_id
            ),
            {"project_name": None},
        )["project_name"]
        return questionary.select(
            message="",
            qmark="Use Meltano Cloud project",
            choices=[x["project_name"] for x in context.projects],
            default=default_project_name,
        ).unsafe_ask()  # Use Click's Ctrl-C handling instead of Questionary's


@project_group.command("use")
@click.option(
    "--name",
    "project_name",
    cls=ProjectChoicesQuestionaryOption,
    help=(
        "The name of a Meltano Cloud project - "
        "see `meltano cloud project list` for the available options."
    ),
    prompt=True,
)
@click.option(
    "--id",
    "project_id",
    help=(
        "The internal ID of a Meltano Cloud project - this ID is unstable and "
        "should only be used if necessary to disambiguate when multiple "
        "projects share a name."
    ),
    default=None,
)
@pass_context
@run_async
async def use_project(
    context: MeltanoCloudCLIContext,
    project_name: str | None,
    project_id: str | None,
) -> None:
    """Set a project as the default to use for Meltano Cloud CLI commands."""
    if project_id is not None and project_name is not None:
        raise click.UsageError("The '--name' and '--id' options are mutually exclusive")
    if project_id is not None:
        context.config.internal_project_id = project_id
        click.secho(
            (
                f"Set the project with ID {project_id!r} as the default "
                "Meltano Cloud project for future commands"
            ),
            fg="green",
        )
        return

    if context.projects is None:  # Interactive config was not used
        context.projects = await _get_projects(context.config)
        _check_for_duplicate_project_names(context.projects)
        if project_name not in {x["project_name"] for x in context.projects}:
            raise click.ClickException(
                f"Unable to use project named {project_name!r} - no available "
                "project matches name.",
            )
    context.config.internal_project_id = next(
        x for x in context.projects if x["project_name"] == project_name
    )["project_id"]
    click.secho(
        (
            f"Set {project_name!r} as the default Meltano Cloud project for "
            "future commands"
        ),
        fg="green",
    )
