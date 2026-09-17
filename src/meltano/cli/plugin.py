"""Plugin management CLI."""

from __future__ import annotations

import json
import typing as t
from dataclasses import asdict, dataclass

import click
from rich.box import SIMPLE_HEAD
from rich.console import Console
from rich.table import Table

from meltano.cli.params import pass_project
from meltano.cli.utils import (
    CliEnvironmentBehavior,
    InstrumentedGroup,
    PartialInstrumentedCmd,
)

if t.TYPE_CHECKING:
    from collections.abc import Iterable

    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project

# Shown in place of a value that could not be determined.
UNKNOWN = "-"

# Marks a plugin that carries its own definition in `meltano.yml`.
CUSTOM = "\u2713"

# Shown in place of a variant that the plugin takes from its parent.
INHERITED = "[dim](inherited)[/dim]"


@dataclass(frozen=True)
class PluginListing:
    """A plugin, as the project defines it."""

    name: str
    type: str
    variant: str | None
    inherited_variant: bool
    custom: bool
    pip_url: str | None
    inherit_from: str | None

    @classmethod
    def from_plugin(cls, plugin: ProjectPlugin) -> PluginListing:
        """Describe a plugin of the project.

        Args:
            plugin: The plugin to describe.

        Returns:
            The plugin listing.
        """
        return cls(
            name=plugin.name,
            type=plugin.type.descriptor,
            variant=plugin.variant,
            # An inheriting plugin resolves its parent's variant unless it
            # names one of its own.
            inherited_variant=bool(plugin.inherit_from) and not plugin.is_variant_set,
            custom=plugin.is_custom(),
            pip_url=plugin.pip_url,
            inherit_from=plugin.inherit_from,
        )


def _render_table(listings: Iterable[PluginListing]) -> None:
    """Print the plugins as a table.

    Args:
        listings: The plugins to print.
    """
    table = Table(box=SIMPLE_HEAD, pad_edge=False)
    table.add_column("TYPE", style="cyan", no_wrap=True)
    table.add_column("NAME", style="bold", overflow="fold")
    table.add_column("VARIANT", overflow="fold")
    table.add_column("INHERITS", overflow="fold")
    table.add_column("CUSTOM", justify="center")

    for listing in listings:
        table.add_row(
            listing.type,
            listing.name,
            INHERITED if listing.inherited_variant else (listing.variant or UNKNOWN),
            listing.inherit_from or "",
            CUSTOM if listing.custom else "",
        )

    Console().print(table)


@click.group(
    cls=InstrumentedGroup,
    name="plugin",
    short_help="Manage project plugins.",
    environment_behavior=CliEnvironmentBehavior.environment_optional_use_default,
)
def plugin() -> None:
    """Manage the plugins in your Meltano project.

    Read more at https://docs.meltano.com/reference/command-line-interface#plugin
    """


@plugin.command(
    cls=PartialInstrumentedCmd,
    name="list",
    short_help="List the plugins in your project.",
)
@click.option(
    "--format",
    "list_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@pass_project()
def list_plugins(project: Project, *, list_format: str) -> None:
    """List the plugins in your project.

    Read more at https://docs.meltano.com/reference/command-line-interface#plugin
    """
    listings = [
        PluginListing.from_plugin(project_plugin)
        for project_plugin in project.plugins.plugins()
        # A mapping is configuration for its mapper, not a separate
        # installation, and is yielded under the mapper's own name.
        if not project_plugin.is_mapping()
    ]
    if list_format == "json":
        click.echo(json.dumps([asdict(listing) for listing in listings], indent=2))
        return

    if listings:
        _render_table(listings)
        return

    click.secho("No plugins are defined in this project.", fg="yellow")
    click.echo("Add one with 'meltano add'.")
