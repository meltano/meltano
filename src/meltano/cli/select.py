import os
import click
import fnmatch
import json
import logging

from . import cli
from .params import project
from meltano.core.config_service import ConfigService
from meltano.core.plugin_invoker import invoker_factory
from meltano.core.plugin.error import PluginExecutionError
from meltano.core.plugin.singer.catalog import parse_select_pattern, SelectionType
from meltano.core.select_service import SelectService
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.db import project_engine


def selection_color(selection):
    if selection is SelectionType.SELECTED:
        return "bright_green"
    elif selection is SelectionType.AUTOMATIC:
        return "bright_white"
    elif selection is SelectionType.EXCLUDED:
        return "red"


def selection_mark(selection):
    """
    Returns the mark to indicate the selection type of an attribute.

    Examples:
      [automatic]
      [selected ]
      [excluded ]
    """

    colwidth = max(map(len, SelectionType))  # size of the longest mark
    return f"[{selection:<{colwidth}}]"


@cli.command()
@click.argument("extractor")
@click.argument("entities_filter", default="*")
@click.argument("attributes_filter", default="*")
@click.option("--list", is_flag=True)
@click.option("--all", is_flag=True)
@click.option("--exclude", is_flag=True)
@project(migrate=True)
def select(project, extractor, entities_filter, attributes_filter, **flags):
    try:
        if flags["list"]:
            show(project, extractor, show_all=flags["all"])
        else:
            add(
                project,
                extractor,
                entities_filter,
                attributes_filter,
                exclude=flags["exclude"],
            )

        tracker = GoogleAnalyticsTracker(project)
        tracker.track_meltano_select(
            extractor=extractor,
            entities_filter=entities_filter,
            attributes_filter=attributes_filter,
            flags=flags,
        )
    except PluginExecutionError as e:
        logging.exception(e)
        raise click.ClickException(
            f"Cannot list the selected properties: "
            "there was a problem running the tap with `--discover`. "
            "Make sure the tap supports `--discover` and run "
            "`meltano invoke {extractor} --discover` to make "
            "sure it runs correctly."
        ) from e
    except Exception as e:
        raise click.ClickException(str(e)) from e


def add(project, extractor, entities_filter, attributes_filter, exclude=False):
    select_service = SelectService(project, extractor)
    select_service.select(entities_filter, attributes_filter, exclude)


def show(project, extractor, show_all=False):
    _, Session = project_engine(project)
    select_service = SelectService(project, extractor)

    try:
        session = Session()
        list_all = select_service.list_all(session)
    finally:
        session.close()

    # legend
    click.secho("Legend:")
    for sel_type in SelectionType:
        click.secho(f"\t{sel_type}", fg=selection_color(sel_type))

    # report
    click.secho("\nEnabled patterns:")
    for select in map(parse_select_pattern, select_service.extractor.select):
        click.secho(
            f"\t{select.property_pattern}", fg="red" if select.negated else "white"
        )

    click.secho("\nSelected properties:")
    for stream, prop in (
        (stream, prop)
        for stream in list_all.streams
        for prop in list_all.properties[stream.key]
    ):
        entry_selection = stream.selection + prop.selection
        mark = selection_mark(entry_selection)
        if show_all or entry_selection:
            click.secho(f"\t{mark} ", fg=selection_color(entry_selection), nl=False)
            click.secho(stream.key, fg=selection_color(stream.selection), nl=False)
            click.secho(f".{prop.key}", fg=selection_color(entry_selection))
