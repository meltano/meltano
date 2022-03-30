"""Extractor selection management CLI."""

from typing import Dict

import click

from meltano.core.db import project_engine
from meltano.core.plugin.error import PluginExecutionError
from meltano.core.plugin.singer.catalog import SelectionType, SelectPattern
from meltano.core.select_service import SelectService
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.utils import click_run_async

from . import cli
from .params import pass_project
from .utils import CliError


def selection_color(selection):
    """Return the appropriate colour for given SelectionType."""
    if selection is SelectionType.SELECTED:
        return "bright_green"
    elif selection is SelectionType.AUTOMATIC:
        return "bright_white"
    elif selection is SelectionType.EXCLUDED:
        return "red"


def selection_mark(selection):
    """
    Return the mark to indicate the selection type of an attribute.

    Examples:
      [automatic]
      [selected ]
      [excluded ]
    """
    colwidth = max(map(len, SelectionType))  # size of the longest mark
    return f"[{selection:<{colwidth}}]"


@cli.command(short_help="Manage extractor selection patterns.")
@click.argument("extractor")
@click.argument("entities_filter", default="*")
@click.argument("attributes_filter", default="*")
@click.option("--list", is_flag=True, help="List the current selected tap attributes.")
@click.option(
    "--all",
    is_flag=True,
    help="Show all the tap attributes with their selected status.",
)
@click.option(
    "--rm",
    "--remove",
    "remove",
    is_flag=True,
    help="Remove previously added select patterns.",
)
@click.option(
    "--exclude",
    is_flag=True,
    help="Exclude all attributes that match specified pattern.",
)
@pass_project(migrate=True)
@click_run_async
async def select(
    project,
    extractor,
    entities_filter,
    attributes_filter,
    **flags: Dict[str, bool],
):
    """
    Manage extractor selection patterns.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#select
    """
    try:
        if flags["list"]:
            await show(project, extractor, show_all=flags["all"])
        else:
            update(
                project,
                extractor,
                entities_filter,
                attributes_filter,
                exclude=flags["exclude"],
                remove=flags["remove"],
            )

        tracker = GoogleAnalyticsTracker(project)
        tracker.track_meltano_select(
            extractor=extractor,
            entities_filter=entities_filter,
            attributes_filter=attributes_filter,
            flags=flags,
        )
    except PluginExecutionError as err:
        raise CliError(f"Cannot list the selected attributes: {err}") from err


def update(
    project, extractor, entities_filter, attributes_filter, exclude=False, remove=False
):
    """Update select pattern for a specific extractor."""
    select_service = SelectService(project, extractor)
    select_service.update(entities_filter, attributes_filter, exclude, remove)


async def show(project, extractor, show_all=False):
    """Show selected."""
    _, Session = project_engine(project)  # noqa: N806
    select_service = SelectService(project, extractor)

    session = Session()
    try:
        list_all = await select_service.list_all(session)
    finally:
        session.close()

    # legend
    click.secho("Legend:")
    for sel_type in SelectionType:
        click.secho(f"\t{sel_type}", fg=selection_color(sel_type))

    # report
    click.secho("\nEnabled patterns:")

    select_pattern: SelectPattern
    for select_pattern in map(SelectPattern.parse, select_service.current_select):
        color = "red" if select_pattern.negated else "white"
        click.secho(f"\t{select_pattern.raw}", fg=color)

    click.secho("\nSelected attributes:")
    for stream, prop in tuple(
        (stream, prop)
        for stream in sorted(list_all.streams)
        for prop in sorted(list_all.properties[stream.key])
    ):
        entry_selection = stream.selection + prop.selection
        mark = selection_mark(entry_selection)
        if show_all or entry_selection:
            click.secho(f"\t{mark} ", fg=selection_color(entry_selection), nl=False)
            click.secho(stream.key, fg=selection_color(stream.selection), nl=False)
            click.secho(f".{prop.key}", fg=selection_color(entry_selection))
