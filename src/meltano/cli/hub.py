"""Meltano Hub command."""

from __future__ import annotations

import json
import typing as t
from collections import Counter
from dataclasses import asdict, dataclass

import click
from rich.box import SIMPLE_HEAD
from rich.console import Console
from rich.table import Table

from meltano.cli.params import PluginTypeArg, pass_project
from meltano.cli.utils import CliEnvironmentBehavior, InstrumentedCmd, InstrumentedGroup
from meltano.core.plugin import PluginType

if t.TYPE_CHECKING:
    from collections.abc import Sequence

    from meltano.core.hub.schema import IndexedPlugin
    from meltano.core.project import Project


@click.group(
    cls=InstrumentedGroup,
    short_help="Interact with Meltano Hub.",
    environment_behavior=CliEnvironmentBehavior.environment_optional_use_default,
)
def hub() -> None:
    """Interact with Meltano Hub.
    Read more at https://docs.meltano.com/reference/command-line-interface#hub
    """  # noqa: D205, D415


@hub.command(
    cls=InstrumentedCmd,
    short_help="Ping Meltano Hub.",
)
@pass_project()
def ping(project: Project) -> None:
    """Ping Meltano Hub. This can be useful for checking if a custom Hub URL is reachable.
    Read more at https://docs.meltano.com/reference/command-line-interface#hub
    """  # noqa: E501, D205, D415
    try:
        # We want to ensure that we can actually communicate with the Hub.
        # Requesting a list of plugins is a good way to do that, but we don't
        # want to waste bandwidth, so we request the list of orchestrators,
        # which is currently very small.
        project.hub_service.get_plugins_of_type(PluginType.ORCHESTRATORS)
    except Exception as ex:
        raise click.ClickException(  # noqa: TRY003
            f"Failed to connect to the Hub at {project.hub_service.hub_api_url!r}",  # noqa: EM102
        ) from ex
    else:
        click.secho(
            f"Successfully connected to the Hub at {project.hub_service.hub_api_url!r}",
            fg="green",
        )


@dataclass(frozen=True)
class HubPluginListing:
    """A variant of a plugin that Meltano Hub offers."""

    type: str
    name: str
    variant: str
    default: bool


# Marks the variant that Meltano Hub installs when none is asked for.
DEFAULT = "[green](default)[/green]"


def _variants(plugin: IndexedPlugin, *, all_variants: bool) -> list[str]:
    """Order the variants of a plugin to list.

    Args:
        plugin: The indexed plugin.
        all_variants: Whether to list every variant rather than the default.

    Returns:
        The variant names, the default one first.
    """
    if not all_variants:
        return [plugin.default_variant]

    others = sorted(set(plugin.variants) - {plugin.default_variant})
    return [plugin.default_variant, *others]


def _render_table(listings: Sequence[HubPluginListing], title: str) -> None:
    """Print the plugins as a table.

    Args:
        listings: The plugins to print.
        title: The line to print above the table.
    """
    table = Table(box=SIMPLE_HEAD, pad_edge=False, title=title, title_justify="left")
    table.add_column("TYPE", style="cyan", no_wrap=True)
    table.add_column("NAME", style="bold", overflow="fold")
    table.add_column("VARIANT", overflow="fold")

    # Naming the default tells a reader nothing where the plugin offers no
    # other variant to choose instead.
    rows = Counter((listing.type, listing.name) for listing in listings)
    previous: tuple[str, str] | None = None

    for listing in listings:
        plugin = (listing.type, listing.name)
        marked = listing.default and rows[plugin] > 1
        # The variants of a plugin are listed together, so a row that repeats
        # the one above it leaves the plugin unnamed.
        repeated = plugin == previous
        previous = plugin

        table.add_row(
            "" if repeated else listing.type,
            "" if repeated else listing.name,
            f"{listing.variant} {DEFAULT}" if marked else listing.variant,
        )

    Console().print(table)


@hub.command(
    cls=InstrumentedCmd,
    name="list",
    short_help="List the plugins available on Meltano Hub.",
)
@click.argument("pattern", required=False)
@click.option(
    "--plugin-type",
    type=PluginTypeArg(),
    help="List only plugins of this type.",
)
@click.option(
    "--all",
    "all_variants",
    is_flag=True,
    help="List every variant of each plugin, rather than only the default one.",
)
@click.option(
    "--format",
    "list_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@pass_project()
def list_plugins(
    project: Project,
    pattern: str | None,
    *,
    plugin_type: PluginType | None,
    all_variants: bool,
    list_format: str,
) -> None:
    """List the plugins that Meltano Hub offers, or those matching PATTERN.

    Read more at https://docs.meltano.com/reference/command-line-interface#hub
    """
    # The Hub indexes one plugin type at a time, so listing every type costs a
    # request for each of them.
    plugin_types = (
        [plugin_type]
        if plugin_type
        else [candidate for candidate in PluginType if candidate.discoverable]
    )

    listings = [
        HubPluginListing(
            type=candidate.descriptor,
            name=plugin.name,
            variant=variant,
            default=variant == plugin.default_variant,
        )
        for candidate in plugin_types
        for plugin in sorted(
            project.hub_service.get_plugins_of_type(candidate).values(),
            key=lambda plugin: plugin.name,
        )
        if pattern is None or pattern.casefold() in plugin.name.casefold()
        for variant in _variants(plugin, all_variants=all_variants)
    ]

    if list_format == "json":
        click.echo(json.dumps([asdict(listing) for listing in listings], indent=2))
        return

    # Name what a row is: the type where one was asked for, and a variant
    # rather than a plugin where every variant is listed.
    noun = plugin_type.descriptor if plugin_type else "plugin"
    if all_variants:
        noun = f"{noun} variant"

    summary = f"{len(listings)} {noun}{'' if len(listings) == 1 else 's'}"
    if pattern:
        summary += f" matching {pattern!r}"

    if not listings:
        click.secho(summary, fg="yellow")
        return

    _render_table(listings, summary)
