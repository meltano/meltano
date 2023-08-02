"""Meltano Hub command."""

from __future__ import annotations

import typing as t

import click

from meltano.cli.params import pass_project
from meltano.cli.utils import CliEnvironmentBehavior, InstrumentedCmd, InstrumentedGroup
from meltano.core.plugin import PluginType

if t.TYPE_CHECKING:
    from meltano.core.project import Project


@click.group(
    cls=InstrumentedGroup,
    short_help="Interact with Meltano Hub.",
    environment_behavior=CliEnvironmentBehavior.environment_optional_use_default,
)
def hub():
    """
    Interact with Meltano Hub.
    Read more at https://docs.meltano.com/reference/command-line-interface#hub
    """  # noqa: D205


@hub.command(
    cls=InstrumentedCmd,
    short_help="Ping Meltano Hub.",
)
@pass_project()
def ping(project: Project):
    """
    Ping Meltano Hub. This can be useful for checking if a custom Hub URL is reachable.
    Read more at https://docs.meltano.com/reference/command-line-interface#hub
    """  # noqa: D205
    try:
        # We want to ensure that we can actually communicate with the Hub.
        # Requesting a list of plugins is a good way to do that, but we don't
        # want to waste bandwidth, so we request the list of orchestrators,
        # which is currently very small.
        project.hub_service.get_plugins_of_type(PluginType.ORCHESTRATORS)
    except Exception as ex:
        raise click.ClickException(
            f"Failed to connect to the Hub at {project.hub_service.hub_api_url!r}",
        ) from ex
    else:
        click.secho(
            f"Successfully connected to the Hub at {project.hub_service.hub_api_url!r}",
            fg="green",
        )
