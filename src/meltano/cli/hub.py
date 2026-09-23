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
from structlog.stdlib import get_logger

from meltano.cli.params import PluginTypeArg, pass_project
from meltano.cli.utils import CliEnvironmentBehavior, InstrumentedCmd, InstrumentedGroup
from meltano.core.cloud.config import CLOUD_API_ROOT
from meltano.core.error import MeltanoError
from meltano.core.plugin import PluginType

logger = get_logger(__name__)


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
    except MeltanoError:
        # A Hub error already names the URL, the cause, and what to do next,
        # so replacing it here would throw that away.
        raise
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


def _variants(plugin: IndexedPlugin) -> list[str]:
    """Order the variants of a plugin.

    Args:
        plugin: The indexed plugin.

    Returns:
        The variant names, the default one first.
    """
    others = sorted(set(plugin.variants) - {plugin.default_variant})
    return [plugin.default_variant, *others]


def _render_table(listings: Sequence[HubPluginListing]) -> None:
    """Print the plugins as a table.

    Args:
        listings: The plugins to print.
    """
    table = Table(box=SIMPLE_HEAD, pad_edge=False)
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
@click.option(
    "--refresh",
    is_flag=True,
    help="Fetch a fresh index rather than a cached one.",
)
@pass_project()
def list_plugins(
    project: Project,
    pattern: str | None,
    *,
    plugin_type: PluginType | None,
    all_variants: bool,
    list_format: str,
    refresh: bool,
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
            project.hub_service.get_plugins_of_type(
                candidate,
                refresh=refresh,
            ).values(),
            key=lambda plugin: plugin.name,
        )
        for variant in _variants(plugin)
    ]

    if pattern:
        # A row is kept where the reader can see what they searched for in it.
        needle = pattern.casefold()
        listings = [
            listing
            for listing in listings
            if needle in listing.name.casefold() or needle in listing.variant.casefold()
        ]

    # Every variant was gathered so that the ones left out can be counted.
    hidden = 0
    if not all_variants:
        defaults = [listing for listing in listings if listing.default]
        hidden = len(listings) - len(defaults)
        listings = defaults

    # Name what a row is: the type where one was asked for, and a variant
    # rather than a plugin where every variant is listed.
    noun = plugin_type.descriptor if plugin_type else "plugin"
    if all_variants:
        noun = f"{noun} variant"

    summary = f"{len(listings)} {noun}{'' if len(listings) == 1 else 's'}"
    if pattern:
        summary += f" {'matches' if len(listings) == 1 else 'match'} {pattern!r}"

    # A search reports what it left out, because a variant that matches is
    # invisible until every variant is listed.
    if pattern and hidden:
        summary += (
            f" ({hidden} variant{'' if hidden == 1 else 's'} hidden, show with '--all')"
        )

    # The count is logged rather than printed, so that it reaches a reader
    # whichever format the rows themselves are in.
    if listings:
        logger.info(summary)
    else:
        logger.warning(summary)

    if list_format == "json":
        click.echo(json.dumps([asdict(listing) for listing in listings], indent=2))
    elif listings:
        _render_table(listings)

    # The Cloud index lists only the plugins that Meltano supports, so a plugin
    # that the reader looks for can be missing from it.
    if project.hub_service.hub_api_url == CLOUD_API_ROOT:
        click.secho(
            "Something missing? Contact the team at support@meltano.com",
            fg="bright_yellow",
            err=True,
        )
