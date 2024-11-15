"""Extractor selection management CLI."""

from __future__ import annotations

import typing as t
from contextlib import closing

import click

from meltano.cli.params import InstallPlugins, get_install_options, pass_project
from meltano.cli.utils import CliEnvironmentBehavior, CliError, InstrumentedCmd
from meltano.core.db import project_engine
from meltano.core.plugin.error import PluginExecutionError
from meltano.core.plugin.singer.catalog import SelectionType, SelectPattern
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.select_service import SelectService
from meltano.core.utils import run_async

if t.TYPE_CHECKING:
    from meltano.core.project import Project


install, no_install, only_install = get_install_options(include_only_install=True)


def selection_color(selection: SelectionType) -> str | None:
    """Return the appropriate colour for given SelectionType."""
    # TODO: Use a match statement when we drop Python 3.9 support
    if selection is SelectionType.SELECTED:
        return "bright_green"
    if selection is SelectionType.AUTOMATIC:
        return "bright_white"
    if selection is SelectionType.EXCLUDED:
        return "red"
    if selection is SelectionType.UNSUPPORTED:
        return "black"

    return None  # pragma: no cover


def selection_mark(selection) -> str:  # noqa: ANN001
    """Return the mark to indicate the selection type of an attribute.

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
@click.argument("entities_filter", default="*")
@click.argument("attributes_filter", default="*")
@click.option("--list", is_flag=True, help="List the current selected tap attributes.")
@click.option(
    "--all",
    is_flag=True,
    help="Show all the tap attributes with their selected status.",
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
    help="Exclude all attributes that match specified pattern.",
)
@install
@no_install
@only_install
@pass_project(migrate=True)
@run_async
async def select(
    project: Project,
    extractor: str,
    entities_filter: str,
    attributes_filter: str,
    install_plugins: InstallPlugins,
    **flags: bool,
) -> None:
    """Manage extractor selection patterns.

    \b
    Read more at https://docs.meltano.com/reference/command-line-interface#select
    """  # noqa: D301
    try:
        if flags["list"]:
            await show(
                project,
                extractor,
                install_plugins=install_plugins,
                show_all=flags["all"],
                refresh=flags["refresh_catalog"],
            )
        else:
            update(
                project,
                extractor,
                entities_filter,
                attributes_filter,
                exclude=flags["exclude"],
                remove=flags["remove"],
            )
    except PluginExecutionError as err:
        raise CliError(f"Cannot list the selected attributes: {err}") from err  # noqa: EM102


def update(
    project: Project,
    extractor: str,
    entities_filter: str,
    attributes_filter: str,
    *,
    exclude: bool = False,
    remove: bool = False,
) -> None:
    """Update select pattern for a specific extractor."""
    select_service = SelectService(project, extractor)
    select_service.update(entities_filter, attributes_filter, exclude, remove=remove)


async def show(
    project: Project,
    extractor: str,
    install_plugins: InstallPlugins,
    *,
    show_all: bool = False,
    refresh: bool = False,
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
