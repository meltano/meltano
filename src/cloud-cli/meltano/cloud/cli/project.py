"""Meltano Cloud `project` command."""

from __future__ import annotations

import json
import sys
import typing as t
from http import HTTPStatus

import click
import tabulate
from ulid import ULID

from meltano.cloud.api.client import MeltanoCloudClient, MeltanoCloudError
from meltano.cloud.cli.base import pass_context, run_async

if t.TYPE_CHECKING:
    from meltano.cloud.api.config import MeltanoCloudConfig
    from meltano.cloud.api.types import CloudProject
    from meltano.cloud.cli.base import MeltanoCloudCLIContext

DEFAULT_GET_PROJECTS_LIMIT = 10
MAX_PAGE_SIZE = 250


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
            "active": x["project_id"] == config.internal_project_id,
        }
        for x in results[:limit]
    ]


def _process_table_row(project: CloudProject) -> tuple[str, ...]:
    return (
        "X" if project["active"] else "",
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
            "Active",
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


async def _get_project_to_activate(
    config: MeltanoCloudConfig,
    identifier: str,
) -> list[CloudProject]:
    try:
        ULID.from_str(identifier)
    except ValueError:
        return await _get_projects(config=config, project_name=identifier)
    try:
        return await _get_projects(config=config, project_id=identifier)
    except MeltanoCloudError as ex:
        if ex.response.status == HTTPStatus.NOT_FOUND:
            # The provided identifier looks like an ID, but isn't one.
            return await _get_projects(config=config, project_name=identifier)
        raise


@project_group.command("activate")
@click.argument("identifier")
@pass_context
@run_async
async def activate_project(
    context: MeltanoCloudCLIContext,
    identifier: str,
) -> None:
    """Set a project as active within the current Meltano Cloud session."""
    projects = await _get_project_to_activate(context.config, identifier)
    if len(projects) > 1:
        click.secho(
            "Unable to uniquely identify a Meltano Cloud project. "
            "Please specify the project using its internal ID, shown below. "
            "Note that these IDs may change at any time. "
            "To avoid this issue, please use unique project names.",
            fg="red",
        )
        for project in projects:
            click.echo(f"{project['project_id']}: {project['project_name']}")
        sys.exit(1)
    context.config.internal_project_id = projects[0]["project_id"]
    click.secho(
        f"Activated Meltano Cloud project {projects[0]['project_name']!r}",
        fg="green",
    )
