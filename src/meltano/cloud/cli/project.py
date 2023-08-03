"""Meltano Cloud `project` command."""

from __future__ import annotations

import asyncio
import logging
import sys
import typing as t
from http import HTTPStatus

import click
import questionary
import requests
from yaspin import yaspin

from meltano.cloud.api.client import MeltanoCloudClient, MeltanoCloudError
from meltano.cloud.cli.base import (
    LimitedResult,
    get_paginated,
    pass_context,
    print_formatted_list,
)
from meltano.core.utils import run_async

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

    async def create_project(
        self,
        project_name: str,
        git_repository: str,
        project_root_path: str | None = None,
    ):
        """Use POST to create new Meltano Cloud project."""
        async with self.authenticated():
            payload = {"project_name": project_name, "git_repository": git_repository}
            if project_root_path:
                payload["project_root_path"] = project_root_path
            prepared_request = await self._json_request(
                "POST",
                f"/projects/v1/{self.config.tenant_resource_key}",
                json=payload,
            )
            response = requests.request(**t.cast(t.Dict[str, t.Any], prepared_request))
            response.raise_for_status()
            return response


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
) -> LimitedResult[CloudProject]:
    async with ProjectsCloudClient(config=config) as client:
        results = await get_paginated(
            lambda page_size, page_token: client.get_projects(
                project_id=project_id,
                project_name=project_name,
                page_size=page_size,
                page_token=page_token,
            ),
            limit,
            MAX_PAGE_SIZE,
        )

    results.items = [
        {
            **x,
            "default": x["project_id"] == _safe_get_internal_project_id(config),
        }
        for x in results.items
    ]
    return results


def _format_project(project: dict[str, t.Any]) -> tuple[str, ...]:
    return (
        "X" if project["default"] else "",
        project["project_name"],
        project["git_repository"],
    )


private_project_attributes = {"tenant_resource_key", "project_id"}


def _remove_private_project_attributes(project: CloudProject) -> dict[str, t.Any]:
    return {k: v for k, v in project.items() if k not in private_project_attributes}


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
    results = await _get_projects(config=context.config, limit=limit)
    stripped_results = LimitedResult(
        items=[_remove_private_project_attributes(x) for x in results.items],
        truncated=results.truncated,
    )
    print_formatted_list(
        stripped_results,
        output_format,
        _format_project,
        ("Default", "Name", "Git Repository"),
        ("center", "left", "left"),
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

        context: MeltanoCloudCLIContext = ctx.obj
        context.projects = asyncio.run(_get_projects(context.config)).items
        _check_for_duplicate_project_names(context.projects)
        default_project_name = next(
            (
                x
                for x in context.projects
                if x["project_id"]
                == context.config.internal_organization_default["default_project_id"]
            ),
            {"project_name": None},
        )["project_name"]
        if not context.projects:
            raise click.ClickException(
                "No Meltano Cloud projects available to use. Please create a "
                "project before running 'meltano cloud project use'.",
            )
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
        context.projects = (await _get_projects(context.config)).items
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


@project_group.command("create")
@click.option("--project-name", type=str, required=True)
@click.option("--git-repository", type=str, required=True)
@click.option("--project-root-path", type=str, required=False)
@pass_context
@run_async
async def create_project(
    context: MeltanoCloudCLIContext,
    project_name: str,
    git_repository: str,
    project_root_path: str | None = None,
):
    """Create a project to your Meltano Cloud."""
    async with ProjectsCloudClient(config=context.config) as client:
        try:
            with yaspin(
                text="Creating project - this may take several minutes...",
            ):
                response = await client.create_project(
                    project_name=project_name,
                    git_repository=git_repository,
                    project_root_path=project_root_path,
                )
        except MeltanoCloudError as e:
            if e.response.status == HTTPStatus.CONFLICT:
                click.secho(
                    f"Project with name {project_name} already exists.",
                    fg="yellow",
                )
            return None
        click.echo(f"Project {project_name} created successfully.")
        if response.status_code == HTTPStatus.NO_CONTENT:
            return None
        click.echo(response.json())
