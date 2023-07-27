"""Meltano Cloud `deployment` command."""

from __future__ import annotations

import asyncio
import json
import platform
import typing as t
from contextlib import contextmanager
from datetime import datetime
from http import HTTPStatus

import click
import questionary
import requests
from slugify import slugify
from yaspin import yaspin  # type: ignore

from meltano.cloud.api.client import MeltanoCloudClient, MeltanoCloudError
from meltano.cloud.api.config import CloudConfigProject
from meltano.cloud.api.types import CloudDeployment
from meltano.cloud.cli.base import (
    LimitedResult,
    get_paginated,
    pass_context,
    print_formatted_list,
    run_async,
)

if t.TYPE_CHECKING:
    from meltano.cloud.api.config import MeltanoCloudConfig
    from meltano.cloud.cli.base import MeltanoCloudCLIContext

DEFAULT_GET_DEPLOYMENTS_LIMIT = 125
MAX_PAGE_SIZE = 250


def _safe_get_response_json_dict(response: requests.Response) -> dict:
    try:
        response_json = response.json()
    except json.JSONDecodeError:
        return {}
    return response_json if isinstance(response_json, dict) else {}


@contextmanager
def _raise_with_details():
    try:
        yield
    except requests.HTTPError as ex:
        if "detail" in _safe_get_response_json_dict(ex.response):
            raise click.ClickException(ex.response.json()["detail"]) from ex
        raise


class DeploymentsCloudClient(MeltanoCloudClient):
    """A Meltano Cloud client with extensions for deployments."""

    async def deployment_exists(self, deployment_name: str) -> bool:
        """Check if a deployment exists."""
        try:
            await self.get_deployment(deployment_name=deployment_name)
        except MeltanoCloudError as ex:
            if ex.response.status == HTTPStatus.NOT_FOUND:
                return False
            raise
        return True

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
            **deployment,  # type: ignore[misc]
            "default": (
                self.config.internal_project_default["default_deployment_name"]
                == deployment["deployment_name"]
            ),
        }

    async def get_deployments(
        self,
        *,
        page_size: int | None = None,
        page_token: str | None = None,
    ):
        """Use GET to get Meltano Cloud deployments.

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
    ) -> CloudDeployment | None:
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
        response = requests.request(**t.cast(t.Dict[str, t.Any], prepared_request))
        response.raise_for_status()
        if response.status_code == HTTPStatus.NO_CONTENT:
            return None
        deployment = response.json()
        return CloudDeployment(
            {
                **deployment,  # type: ignore[misc]
                "default": (
                    self.config.internal_project_default["default_deployment_name"]
                    == deployment["deployment_name"]
                ),
            },
        )

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
        response = requests.request(**t.cast(t.Dict[str, t.Any], prepared_request))
        response.raise_for_status()


@click.group("deployment")
def deployment_group() -> None:
    """Interact with Meltano Cloud deployments."""


async def _get_deployments(
    config: MeltanoCloudConfig,
    *,
    limit: int = DEFAULT_GET_DEPLOYMENTS_LIMIT,
) -> LimitedResult[CloudDeployment]:
    async with DeploymentsCloudClient(config=config) as client:
        results = await get_paginated(
            lambda page_size, page_token: client.get_deployments(
                page_size=page_size,
                page_token=page_token,
            ),
            limit,
            MAX_PAGE_SIZE,
        )

    results.items = [
        {
            **x,
            "default": x["deployment_name"]
            == config.internal_project_default["default_deployment_name"],
        }
        for x in results.items
    ]

    return results


def _format_deployment(deployment: CloudDeployment) -> tuple[str, ...]:
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
    results = await _get_deployments(config=context.config, limit=limit)
    print_formatted_list(
        results,
        output_format,
        _format_deployment,
        (
            "Default",
            "Name",
            "Environment",
            "Tracked Git Rev",
            "Current Git Hash",
            "Last Deployed (UTC)",
        ),
        ("center", "left", "left"),
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
        context.deployments = asyncio.run(_get_deployments(context.config)).items
        return questionary.select(
            message="",
            qmark="Use Meltano Cloud deployment",
            choices=[x["deployment_name"] for x in context.deployments],
        ).unsafe_ask()  # Use Click's Ctrl-C handling instead of Questionary's


@deployment_group.command(
    "use",
    short_help="Set a deployment as the default to use for Meltano Cloud CLI commands.",
)
@click.option(
    "--name",
    "deployment_name",
    cls=DeploymentChoicesQuestionaryOption,
    help=(
        "The name of a Meltano Cloud deployment - "
        "see `meltano cloud deployment list` for the available options."
    ),
    prompt=True,
)
@pass_context
@run_async
async def use_deployment(  # noqa: D103
    context: MeltanoCloudCLIContext,
    deployment_name: str,
) -> None:
    deployment_name = slugify(deployment_name)
    if context.deployments is None:  # Interactive config was not used
        context.deployments = (await _get_deployments(context.config)).items
        if deployment_name not in {x["deployment_name"] for x in context.deployments}:
            raise click.ClickException(
                f"Unable to use deployment named {deployment_name!r} - no available "
                "Meltano Cloud deployment matches name.",
            )

    _set_project_default_deployment(context, deployment_name)
    context.config.write_to_file()
    click.secho(
        (
            f"Set {deployment_name!r} as the default Meltano Cloud "
            "deployment for future commands"
        ),
        fg="green",
    )


def _set_project_default_deployment(
    context: MeltanoCloudCLIContext,
    deployment_name: str,
) -> None:
    """Set the default deployment in the config for future commands.

    Args:
        context: The Cloud CLI context.
        deployment_name: The name of the deployment to set as the default.
    """
    context.config.internal_project_default = CloudConfigProject(
        default_deployment_name=deployment_name,
    )


@deployment_group.command("create")
@click.option(
    "--name",
    "deployment_name",
    help="A name which uniquely identifies the new Meltano Cloud deployment",
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
    """Create a new Meltano Cloud deployment."""
    deployment_name = slugify(deployment_name)
    async with DeploymentsCloudClient(config=context.config) as client:
        if await client.deployment_exists(deployment_name=deployment_name):
            raise click.ClickException(
                f"Deployment {deployment_name!r} already exists. "
                "Use `meltano cloud deployment update` to update an "
                "existing Meltano Cloud deployment.",
            )
        with yaspin(
            text="Creating deployment - this may take several minutes...",
        ), _raise_with_details():
            deployment = await client.update_deployment(
                deployment_name=deployment_name,
                environment_name=environment_name,
                git_rev=git_rev,
            )
        if deployment is None:
            click.secho(
                "Deployment already exists, and was not updated.",
                fg="yellow",
            )
            return

        new_deployment_name = deployment["deployment_name"]
        deployments = await client.get_deployments(page_size=2)

        if isinstance(deployments, dict) and deployments["results"]:
            results = deployments["results"]
            if isinstance(results, list) and len(results) == 1:
                _set_project_default_deployment(context, new_deployment_name)
                click.secho(
                    (
                        "Created first deployment. "
                        f"Set {new_deployment_name!r} as the "
                        "default Meltano Cloud deployment for future commands"
                    ),
                    fg="green",
                )

                return

        click.secho(
            (
                f'Created deployment "{new_deployment_name}". '
                "To use as default run "
                f'"meltano cloud deployment use --name {new_deployment_name}."'
            ),
            fg="green",
        )


@deployment_group.command(
    "update",
    short_help=(
        "Update a Meltano Cloud deployment, using the latest commit "
        "from the tracked git rev."
    ),
)
@click.option(
    "--name",
    "deployment_name",
    help="A name which uniquely identifies the Meltano Cloud deployment to update",
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
async def update_deployment(  # noqa: D103
    context: MeltanoCloudCLIContext,
    deployment_name: str,
    force: bool,
    preserve_git_hash: bool,
) -> None:
    deployment_name = slugify(deployment_name)
    with yaspin(text="Updating deployment - this may take several minutes..."):
        async with DeploymentsCloudClient(config=context.config) as client:
            try:
                existing_deployment = await client.get_deployment(
                    deployment_name=deployment_name,
                )
            except MeltanoCloudError as ex:
                if ex.response.status == HTTPStatus.NOT_FOUND:
                    raise click.ClickException(
                        f"Deployment {deployment_name!r} does not exist. "
                        "Use `meltano cloud deployment create` to create a "
                        "new Meltano Cloud deployment.",
                    ) from ex
                raise
            with _raise_with_details():
                updated_deployment = await client.update_deployment(
                    deployment_name=deployment_name,
                    environment_name=existing_deployment["environment_name"],
                    git_rev=existing_deployment["git_rev"],
                    force=force,
                    preserve_git_hash=preserve_git_hash,
                )
    if updated_deployment is None:
        click.secho(
            (
                "Deployment already up-to-date. No changes to the Meltano "
                "manifest were detected. Use the '--force' option to perform "
                "an update anyway."
            ),
            fg="yellow",
        )
    else:
        click.secho(
            f"Updated deployment {updated_deployment['deployment_name']!r}",
            fg="green",
        )


@deployment_group.command("delete")
@click.option(
    "--name",
    "deployment_name",
    help="A name which uniquely identifies the new Meltano Cloud deployment",
    prompt=True,
)
@pass_context
@run_async
async def delete_deployment(
    context: MeltanoCloudCLIContext,
    deployment_name: str,
) -> None:
    """Delete a Meltano Cloud deployment."""
    deployment_name = slugify(deployment_name)
    with yaspin(text="Deleting deployment - this may take several minutes..."):
        async with DeploymentsCloudClient(config=context.config) as client:
            if not await client.deployment_exists(deployment_name=deployment_name):
                raise click.ClickException(
                    f"Deployment {deployment_name!r} does not exist.",
                )
            with _raise_with_details():
                await client.delete_deployment(deployment_name=deployment_name)
    click.secho(f"Deleted deployment {slugify(deployment_name)!r}", fg="green")
