import os
import click
import fnmatch
import json

from . import cli
from .params import project
from meltano.core.config_service import ConfigService
from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginExecutionError
from meltano.core.plugin.singer.catalog import parse_select_pattern
from meltano.core.select_service import SelectService
from meltano.core.tracking import GoogleAnalyticsTracker


@cli.command()
@project
@click.argument("extractor")
@click.argument("entities_filter", default="*")
@click.argument("attributes_filter", default="*")
@click.option("--list", is_flag=True)
@click.option("--all", is_flag=True)
@click.option("--exclude", is_flag=True)
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
    select_service = SelectService(project, extractor)
    extractor = select_service.get_extractor()
    list_all = select_service.get_extractor_entities()

    # report
    click.secho("Enabled patterns:")
    for select in map(parse_select_pattern, extractor.select):
        click.secho(
            f"\t{select.property_pattern}", fg="red" if select.negated else "white"
        )
    else:
        click.echo()

    click.secho("Selected properties:")
    color = lambda selected: "white" if selected else "red"
    for stream, prop in (
        (stream, prop)
        for stream in list_all.streams
        for prop in list_all.properties[stream.key]
    ):
        if show_all:
            click.secho(f"\t{stream.key}", fg=color(stream.selected), nl=False)
            click.echo(".", nl=False)
            click.secho(prop.key, fg=color(stream.selected and prop.selected))
        elif stream.selected and prop.selected:
            click.echo(f"\t{stream.key}.{prop.key}")
