"""Extractor selection management CLI."""

from __future__ import annotations

import json
import typing as t
from contextlib import closing

import click

from meltano.cli.params import get_install_options, pass_project
from meltano.cli.utils import CliEnvironmentBehavior, CliError, InstrumentedCmd
from meltano.core.db import project_engine
from meltano.core.plugin.error import PluginExecutionError
from meltano.core.plugin.singer.catalog import SelectionType, SelectPattern
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.select_service import SelectService
from meltano.core.utils import run_async

if t.TYPE_CHECKING:
    from meltano.cli.params import InstallPlugins
    from meltano.core.plugin.singer.catalog import ListSelectedExecutor
    from meltano.core.project import Project


install, no_install, only_install = get_install_options(include_only_install=True)


def selection_color(selection: SelectionType) -> str:
    """Return the appropriate colour for given SelectionType."""
    match selection:
        case SelectionType.SELECTED:
            return "bright_green"
        case SelectionType.AUTOMATIC:
            return "bright_white"
        case SelectionType.EXCLUDED:
            return "red"
        case SelectionType.UNSUPPORTED:
            return "black"
        case _:  # pragma: no cover
            t.assert_never(selection)


def selection_mark(selection: SelectionType) -> str:
    """Return the mark to indicate the selection type of a property.

    Examples:
      [automatic]
      [selected ]
      [excluded ]
    """
    colwidth = max(map(len, SelectionType))  # size of the longest mark
    return f"[{selection:<{colwidth}}]"


@click.command(
    cls=InstrumentedCmd,
    short_help="Manage extractor selection patterns.",
    environment_behavior=CliEnvironmentBehavior.environment_optional_ignore_default,
)
@click.argument("extractor")
@click.argument("streams_filter", default="*")
@click.argument("properties_filter", default="*")
@click.option(
    "--list",
    "list_format",
    flag_value="text",
    default=None,
    help="List the current selected tap properties in plain text format.",
)
@click.option(
    "--json",
    "list_format",
    flag_value="json",
    help="List the current selected tap properties in JSON format.",
)
@click.option(
    "--all",
    "show_all",
    is_flag=True,
    help="Show all the tap properties with their selected status.",
)
@click.option(
    "--refresh-catalog",
    is_flag=True,
    help="Invalidate the catalog cache and refresh the catalog.",
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
    help="Exclude all properties that match specified pattern.",
)
@click.option(
    "--clear",
    is_flag=True,
    help="Clear all select patterns for the extractor.",
)
@install
@no_install
@only_install
@pass_project(migrate=True)
@run_async
async def select(
    project: Project,
    extractor: str,
    streams_filter: str,
    properties_filter: str,
    install_plugins: InstallPlugins,
    *,
    list_format: t.Literal["text", "json"] | None,
    show_all: bool,
    refresh_catalog: bool,
    remove: bool,
    exclude: bool,
    clear: bool,
) -> None:
    """Manage extractor selection patterns.

    \b
    Read more at https://docs.meltano.com/reference/command-line-interface#select
    """  # noqa: D301
    try:
        if clear:
            clear_selections(project, extractor)
        elif list_format is not None:
            await show(
                project,
                extractor,
                install_plugins=install_plugins,
                show_all=show_all,
                refresh=refresh_catalog,
                output_format=list_format,
            )
        else:
            update(
                project,
                extractor,
                streams_filter,
                properties_filter,
                exclude=exclude,
                remove=remove,
            )
    except PluginExecutionError as err:
        raise CliError(f"Cannot list the selected properties: {err}") from err  # noqa: EM102, TRY003


def clear_selections(project: Project, extractor: str) -> None:
    """Clear all select patterns for a specific extractor."""
    select_service = SelectService(project, extractor)
    select_service.clear()


def update(
    project: Project,
    extractor: str,
    streams_filter: str,
    properties_filter: str,
    *,
    exclude: bool = False,
    remove: bool = False,
) -> None:
    """Update select pattern for a specific extractor."""
    select_service = SelectService(project, extractor)
    select_service.update(streams_filter, properties_filter, exclude, remove=remove)


async def show(
    project: Project,
    extractor: str,
    install_plugins: InstallPlugins,
    *,
    show_all: bool = False,
    refresh: bool = False,
    output_format: t.Literal["text", "json"] = "text",
) -> None:
    """Show selected."""
    _, Session = project_engine(project)  # noqa: N806
    select_service = SelectService(project, extractor)

    await install_plugins(  # pragma: no cover
        project,
        [select_service.extractor],
        reason=PluginInstallReason.AUTO,
    )

    with closing(Session()) as session:
        list_all = await select_service.list_all(session, refresh=refresh)

    if output_format == "json":
        _show_json(
            patterns=select_service.current_select,
            list_all=list_all,
            show_all=show_all,
        )
    else:
        _show_plain(
            patterns=select_service.current_select,
            list_all=list_all,
            show_all=show_all,
        )


def _show_json(
    *,
    patterns: list[str],
    list_all: ListSelectedExecutor,
    show_all: bool,
) -> None:
    output: dict[str, list] = {
        "enabled_patterns": [],
        "streams": [],
    }
    for select_pattern in map(SelectPattern.parse, patterns):
        output["enabled_patterns"].append(select_pattern.raw)

    for stream, prop in (
        (strm, prp)
        for strm in sorted(list_all.streams)
        for prp in sorted(list_all.properties[strm.key])
    ):
        entry_selection = stream.selection + prop.selection
        if show_all or entry_selection:
            output["streams"].append(
                {
                    "stream": stream.key,
                    "property": prop.key,
                    "selection": entry_selection,
                }
            )

    click.echo(json.dumps(output, indent=2, default=str))


def _show_plain(
    *,
    patterns: list[str],
    list_all: ListSelectedExecutor,
    show_all: bool,
) -> None:
    # legend
    click.secho("Legend:")
    for sel_type in SelectionType:
        click.secho(f"\t{sel_type}", fg=selection_color(sel_type))

    # report
    click.secho("\nEnabled patterns:")

    for select_pattern in map(SelectPattern.parse, patterns):
        color = "red" if select_pattern.negated else "white"
        click.secho(f"\t{select_pattern.raw}", fg=color)

    click.secho("\nSelected properties:")
    for stream, prop in (
        (strm, prp)
        for strm in sorted(list_all.streams)
        for prp in sorted(list_all.properties[strm.key])
    ):
        entry_selection = stream.selection + prop.selection
        mark = selection_mark(entry_selection)
        if show_all or entry_selection:
            click.secho(f"\t{mark} ", fg=selection_color(entry_selection), nl=False)
            click.secho(stream.key, fg=selection_color(stream.selection), nl=False)
            click.secho(f".{prop.key}", fg=selection_color(entry_selection))
