"""Meltano Cloud `deployment` command."""

from __future__ import annotations

import asyncio
import json
import platform
import typing as t
from datetime import datetime

import click
import questionary
import requests
import tabulate
from slugify import slugify
from yaspin import yaspin

from meltano.cloud.api.client import MeltanoCloudClient
from meltano.cloud.cli.base import pass_context, run_async

if t.TYPE_CHECKING:
    from meltano.cloud.api.config import MeltanoCloudConfig
    from meltano.cloud.api.types import CloudDeployment
    from meltano.cloud.cli.base import MeltanoCloudCLIContext

DEFAULT_GET_DEPLOYMENTS_LIMIT = 125
MAX_PAGE_SIZE = 250


class DeploymentsCloudClient(MeltanoCloudClient):
    """A Meltano Cloud client with extensions for deployments."""

    async def get_deployment(self, deployment_name: str) -> CloudDeployment:
        """Use GET to get a Meltano Cloud deployment.

        Args:
            deployment_name: The name of the deployment to get.
        """
        async with self.authenticated():
            deployment = await self._json_request(
                "GET",
                (
                    "/deployments"
                    "/v1"
                    f"/{self.config.tenant_resource_key}"
                    f"/{self.config.internal_project_id}"
                    f"/{deployment_name}"
                ),
            )
        return {
            **deployment,
            "default": (
                self.config.default_deployment_name == deployment["deployment_name"]
            ),
        }

    async def get_deployments(
        self,
        *,
        page_size: int | None = None,
        page_token: str | None = None,
    ):
        """Use GET to get Meltano Cloud project deployments.

        Args:
            project_id: The ID of the project the deployments are of.
            page_size: The number of items to request per page.
            page_token: The page token.
        """
        async with self.authenticated():
            return await self._json_request(
                "GET",
                (
                    "/deployments"
                    "/v1"
                    f"/{self.config.tenant_resource_key}"
                    f"/{self.config.internal_project_id}"
                ),
                params=self.clean_params(
                    {
                        "page_size": page_size,
                        "page_token": page_token,
                    },
                ),
            )

    async def update_deployment(
        self,
        deployment_name: str,
        environment_name: str,
        git_rev: str,
        force: bool = False,
        preserve_git_hash: bool = False,
    ) -> CloudDeployment:
        """Use POST to update a Meltano Cloud deployment.

        Args:
            deployment_name: The name of the deployment to update.
            environment_name: The name of the environment for the deployment.
            git_rev: The git revision from which to source the project.
            force: Whether to force the update to occur even if no changes are
                detected via the manifest.
            preserve_git_hash: Whether to preserve the git commit hash of the
                deployment, or update it to the latest for the tracked git
                revision.
        """
        async with self.authenticated():
            prepared_request = await self._json_request(
                "POST",
                (
                    "/deployments"
                    "/v1"
                    f"/{self.config.tenant_resource_key}"
                    f"/{self.config.internal_project_id}"
                    f"/{deployment_name}"
                ),
                json={"environment_name": environment_name, "git_rev": git_rev},
                params=self.clean_params(
                    {
                        "force": str(force),
                        "preserve_git_hash": str(preserve_git_hash),
                    },
                ),
            )
        response = requests.request(**prepared_request)
        response.raise_for_status()
        deployment = response.json()["deployment"]
        return {
            **deployment,
            "default": (
                self.config.default_deployment_name == deployment["deployment_name"]
            ),
        }

    async def delete_deployment(self, deployment_name: str) -> None:
        """Use DELETE to delete a Meltano Cloud deployment.

        Args:
            deployment_name: The name of the deployment to delete.
        """
        async with self.authenticated():
            prepared_request = await self._json_request(
                "DELETE",
                (
                    "/deployments"
                    "/v1"
                    f"/{self.config.tenant_resource_key}"
                    f"/{self.config.internal_project_id}"
                    f"/{deployment_name}"
                ),
            )
        response = requests.request(**prepared_request)
        response.raise_for_status()


@click.group("deployment")
def deployment_group() -> None:
    """Interact with Meltano Cloud deployments."""


async def _get_deployments(
    config: MeltanoCloudConfig,
    *,
    limit: int = DEFAULT_GET_DEPLOYMENTS_LIMIT,
) -> list[CloudDeployment]:
    page_token = None
    page_size = min(limit, MAX_PAGE_SIZE)
    results: list[CloudDeployment] = []

    async with DeploymentsCloudClient(config=config) as client:
        while True:
            response = await client.get_deployments(
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
            "default": x["deployment_name"] == config.default_deployment_name,
        }
        for x in results[:limit]
    ]


def _process_table_row(deployment: CloudDeployment) -> tuple[str, ...]:
    return (  # noqa: WPS227
        "X" if deployment["default"] else "",
        deployment["deployment_name"],
        deployment["environment_name"],
        deployment["git_rev"],
        deployment["git_rev_hash"][:7],
        datetime.fromisoformat(deployment["last_deployed_timestamp"]).strftime(
            "%Y-%m-%d %H:%M:%S",
        ),
    )


def _format_deployments_table(
    deployments: list[CloudDeployment],
    table_format: str,
) -> str:
    """Format the deployments as a table.

    Args:
        deployments: The deployments to format.

    Returns:
        The formatted deployments.
    """
    return tabulate.tabulate(
        [_process_table_row(deployment) for deployment in deployments],
        headers=(
            "Default",
            "Name",
            "Environment",
            "Tracked Git Rev",
            "Current Git Hash",
            "Last Deployed (UTC)",
        ),
        tablefmt=table_format,
        # To avoid a tabulate bug (IndexError), only set colalign if there are
        # deployments
        colalign=("center", "left", "left") if deployments else (),
    )


deployment_list_formatters = {
    "json": lambda x: json.dumps(x, indent=2),
    "markdown": lambda x: _format_deployments_table(x, table_format="github"),
    "terminal": lambda x: _format_deployments_table(x, table_format="rounded_outline"),
}


@deployment_group.command("list")
@click.option(
    "--limit",
    required=False,
    type=int,
    default=DEFAULT_GET_DEPLOYMENTS_LIMIT,
    help="The maximum number of deployments to display.",
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
async def list_deployments(
    context: MeltanoCloudCLIContext,
    output_format: str,
    limit: int,
) -> None:
    """List Meltano Cloud deployments."""
    click.echo(
        deployment_list_formatters[output_format](
            await _get_deployments(config=context.config, limit=limit),
        ),
    )


class DeploymentChoicesQuestionaryOption(click.Option):
    """Click option that provides an interactive prompt for a deployment name."""

    def prompt_for_value(self, ctx: click.Context) -> t.Any:
        """Prompt the user to interactively select a deployment by name.

        Args:
            ctx: The Click context.

        Returns:
            The name of the deployment to be used as the default for future commands.
        """
        if platform.system() == "Windows":
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy(),  # type: ignore[attr-defined]
            )

        context: MeltanoCloudCLIContext = ctx.obj
        context.deployments = asyncio.run(_get_deployments(context.config))
        return questionary.select(
            message="",
            qmark="Use Meltano Cloud project deployment",
            choices=[x["deployment_name"] for x in context.deployments],
        ).unsafe_ask()  # Use Click's Ctrl-C handling instead of Questionary's


@deployment_group.command("use")
@click.option(
    "--name",
    "deployment_name",
    cls=DeploymentChoicesQuestionaryOption,
    help=(
        "The name of a Meltano Cloud project deployment - "
        "see `meltano cloud deployment list` for the available options."
    ),
    prompt=True,
)
@pass_context
@run_async
async def use_deployment(
    context: MeltanoCloudCLIContext,
    deployment_name: str | None,
) -> None:
    """Set a deployment as the default to use for Meltano Cloud CLI commands."""
    deployment_name = slugify(deployment_name)
    if context.deployments is None:  # Interactive config was not used
        context.deployments = await _get_deployments(context.config)
        if deployment_name not in {x["deployment_name"] for x in context.deployments}:
            raise click.ClickException(
                f"Unable to use deployment named {deployment_name!r} - no available "
                "Meltano Cloud project deployment matches name.",
            )
    context.config.default_deployment_name = deployment_name
    context.config.write_to_file()
    click.secho(
        (
            f"Set {deployment_name!r} as the default Meltano Cloud project "
            "deployment for future commands"
        ),
        fg="green",
    )


@deployment_group.command("create")
@click.option(
    "--name",
    "deployment_name",
    help="A name which uniquely identifies the new Meltano Cloud project deployment",
    prompt=True,
)
@click.option(
    "--environment",
    "environment_name",
    help="The name of the Meltano environment to be deployed",
    prompt=True,
)
@click.option(
    "--git-rev",
    help=(
        "The git revision this deployment should track, such as a branch name "
        "or commit hash"
    ),
    prompt=True,
)
@pass_context
@run_async
async def create_deployment(
    context: MeltanoCloudCLIContext,
    deployment_name: str,
    environment_name: str,
    git_rev: str,
) -> None:
    """Create a new Meltano Cloud project deployment."""
    with yaspin(text="Creating deployment - this may take several minutes..."):
        async with DeploymentsCloudClient(config=context.config) as client:
            deployment = await client.update_deployment(
                deployment_name=deployment_name,
                environment_name=environment_name,
                git_rev=git_rev,
            )
    click.secho(f"Created deployment {deployment['deployment_name']!r}", fg="green")


@deployment_group.command("update")
@click.option(
    "--name",
    "deployment_name",
    help="A name which uniquely identifies the new Meltano Cloud project deployment",
    prompt=True,
)
@click.option(
    "--force/--no-force",
    help=(
        "Whether to re-deploy the Meltano environment in Meltano Cloud even "
        "if no changes to the project have been detected"
    ),
)
@click.option(
    "--preserve-git-hash/--no-preserve-git-hash",
    help=(
        "The git revision this deployment should track, such as a branch name "
        "or commit hash"
    ),
)
@pass_context
@run_async
async def update_deployment(
    context: MeltanoCloudCLIContext,
    deployment_name: str,
    force: bool,
    preserve_git_hash: bool,
) -> None:
    """Update a Meltano Cloud project deployment, using the latest commit from the tracked git rev."""  # noqa: E501
    with yaspin(text="Updating deployment - this may take several minutes..."):
        async with DeploymentsCloudClient(config=context.config) as client:
            existing_deployment = await client.get_deployment(
                deployment_name=deployment_name,
            )
            updated_deployment = await client.update_deployment(
                deployment_name=deployment_name,
                environment_name=existing_deployment["environment_name"],
                git_rev=existing_deployment["git_rev"],
                force=force,
                preserve_git_hash=preserve_git_hash,
            )
    click.secho(
        f"Updated deployment {updated_deployment['deployment_name']!r}",
        fg="green",
    )


@deployment_group.command("delete")
@click.option(
    "--name",
    "deployment_name",
    help="A name which uniquely identifies the new Meltano Cloud project deployment",
    prompt=True,
)
@pass_context
@run_async
async def delete_deployment(
    context: MeltanoCloudCLIContext,
    deployment_name: str,
) -> None:
    """Delete a Meltano Cloud project deployment."""
    with yaspin(text="Deleting deployment - this may take several minutes..."):
        async with DeploymentsCloudClient(config=context.config) as client:
            await client.delete_deployment(deployment_name=deployment_name)
    click.secho(f"Deleted deployment {slugify(deployment_name)!r}", fg="green")
