"""Plugin Add CLI."""

from __future__ import annotations

import typing as t
from pathlib import Path
from urllib.parse import urlparse

import click
import requests

from meltano.cli.params import PluginTypeArg, get_install_options, pass_project
from meltano.cli.utils import (
    CliError,
    PartialInstrumentedCmd,
    add_plugin,
    add_required_plugins,
    check_dependencies_met,
    infer_plugin_type,
)
from meltano.core.plugin import PluginRef, PluginType
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.project_add_service import ProjectAddService
from meltano.core.tracking.contexts import CliEvent, PluginsTrackingContext
from meltano.core.utils import run_async
from meltano.core.yaml import yaml

if t.TYPE_CHECKING:
    from meltano.cli.params import InstallPlugins
    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project
    from meltano.core.tracking import Tracker

install, no_install = get_install_options(include_only_install=False)


def _load_yaml_from_ref(
    ctx: click.Context,
    param: click.Parameter,
    value: str | None,
) -> dict | None:
    if not value:
        return None

    try:
        url = urlparse(value)
        if url.scheme and url.netloc:
            response = requests.get(value, timeout=10)
            response.raise_for_status()
            content = response.text
        else:
            content = Path(value).read_text()

    except (ValueError, FileNotFoundError, IsADirectoryError) as e:
        raise click.BadParameter(str(e), ctx=ctx, param=param) from e

    return yaml.load(content) or {}


@click.command(
    cls=PartialInstrumentedCmd,
    short_help="Add a plugin to your project.",
)
@click.argument("plugin", nargs=-1, required=True)
@click.option("--plugin-type", type=PluginTypeArg())
@click.option(
    "--inherit-from",
    help=(
        "Add a plugin inheriting from an existing plugin in the project"
        " or a discoverable plugin identified, by name."
    ),
)
@click.option(
    "--variant",
    help="Add a specific (non-default) variant of the identified discoverable plugin.",
)
@click.option(
    "--as",
    "as_name",
    help=(
        "Shorthand for '--inherit-from', that can be used to add a "
        "discoverable plugin to your project with a different name. "
        "Usage:\b\n\nadd <type> <inherit-from> --as <name>"
    ),
)
@click.option(
    "--from-ref",
    "plugin_yaml",
    callback=_load_yaml_from_ref,
    help="Reference a plugin definition to add from.",
)
@click.option(
    "--python",
    help=(
        "The Python version to use for the plugin. Only applies to base plugins which "
        "have Python virtual environments, rather than inherited plugins which use the "
        "virtual environment of their base plugin, or plugins that run in a container."
    ),
)
@click.option(
    "--custom",
    is_flag=True,
    help=(
        "Add a custom plugin. The command will prompt you for the package's "
        "base plugin description metadata."
    ),
)
@click.option(
    "--update/--no-update",
    is_flag=True,
    default=True,
    help="Update an existing plugin.",
    hidden=True,
)
@install
@no_install
@click.option(
    "--force-install",
    is_flag=True,
    help="Ignore the required Python version declared by the plugins.",
)
@pass_project()
@click.pass_context
@run_async
async def add(
    ctx: click.Context,
    project: Project,
    plugin: tuple[str, ...],
    install_plugins: InstallPlugins,
    plugin_type: PluginType | None,
    inherit_from: str | None,
    variant: str | None,
    as_name: str | None,
    plugin_yaml: dict | None,
    python: str | None,
    **flags: bool,
) -> None:
    """Add a plugin to your project.

    \b
    Read more at https://docs.meltano.com/reference/command-line-interface#add
    """  # noqa: D301
    tracker: Tracker = ctx.obj["tracker"]

    plugin_names = plugin

    if as_name:
        # `add <type> <inherit-from> --as <name>``
        # is equivalent to:
        # `add <type> <name> --inherit-from <inherit-from>``
        inherit_from = plugin_names[0]
        plugin_names = (as_name,)

    if flags["custom"] and plugin_type in {
        PluginType.TRANSFORMS,
        PluginType.ORCHESTRATORS,
    }:
        tracker.track_command_event(CliEvent.aborted)
        raise CliError(f"--custom is not supported for {plugin_type}")  # noqa: EM102, TRY003

    plugin_refs: list[PluginRef] = [
        PluginRef(
            plugin_type=infer_plugin_type(name) if plugin_type is None else plugin_type,
            name=name,
        )
        for name in plugin_names
    ]
    dependencies_met, err = check_dependencies_met(
        plugin_refs=plugin_refs,
        plugins_service=project.plugins,
    )
    if not dependencies_met:
        tracker.track_command_event(CliEvent.aborted)
        raise CliError(f"Failed to install plugin(s): {err}")  # noqa: EM102, TRY003

    add_service = ProjectAddService(project)

    plugins: list[ProjectPlugin] = []
    for ref in plugin_refs:
        try:
            plugins.append(
                add_plugin(
                    ref.type,
                    ref.name,
                    python=python,
                    inherit_from=inherit_from,
                    variant=variant,
                    custom=flags["custom"],
                    update=flags["update"],
                    add_service=add_service,
                    plugin_yaml=plugin_yaml,
                ),
            )
        except Exception:
            # if the plugin is not known to meltano send what information we do have
            tracker.add_contexts(
                PluginsTrackingContext([(plugin, None) for plugin in plugins]),
            )
            tracker.track_command_event(CliEvent.aborted)
            raise

        required_plugins = add_required_plugins(
            plugins,
            add_service=add_service,
        )
    plugins.extend(required_plugins)
    tracker.add_contexts(
        PluginsTrackingContext([(candidate, None) for candidate in plugins]),
    )
    tracker.track_command_event(CliEvent.inflight)

    success = await install_plugins(
        project,
        plugins,
        reason=PluginInstallReason.ADD,
        force=flags.get("force_install", False),
    )

    if success is False:
        tracker.track_command_event(CliEvent.failed)
        raise CliError("Failed to install plugin(s)")  # noqa: EM101, TRY003

    _print_plugins(plugins)
    tracker.track_command_event(CliEvent.completed)


def _print_plugins(plugins: list[ProjectPlugin]) -> None:
    printed_empty_line = False
    for plugin in plugins:
        docs_url = plugin.docs or plugin.repo
        if not docs_url:
            continue

        if not printed_empty_line:
            click.echo()
            printed_empty_line = True

        click.echo(
            f"To learn more about {plugin.type.descriptor} '{plugin.name}', "
            f"visit {docs_url}",
        )
