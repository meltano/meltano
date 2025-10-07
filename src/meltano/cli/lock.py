"""Lock command."""

from __future__ import annotations

import typing as t
import warnings

import click
import structlog

from meltano.cli.params import PluginTypeArg, pass_project
from meltano.cli.utils import CliError, PartialInstrumentedCmd
from meltano.core.plugin_lock_service import (
    LockfileAlreadyExistsError,
    PluginLock,
    PluginLockService,
)
from meltano.core.project_plugins_service import DefinitionSource
from meltano.core.tracking.contexts import CliEvent, PluginsTrackingContext

if t.TYPE_CHECKING:
    from meltano.core.plugin import PluginType
    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project
    from meltano.core.tracking import Tracker


__all__ = ["lock"]
logger = structlog.get_logger(__name__)


@click.command(cls=PartialInstrumentedCmd, short_help="Lock plugin definitions.")
@click.option(
    "--all",
    "all_plugins",
    is_flag=True,
    hidden=True,
    help="DEPRECATED: All plugins are now locked by default.",
)
@click.option(
    "--plugin-type",
    type=PluginTypeArg(),
    help="Lock only the plugins of the given type.",
)
@click.argument("plugin_name", nargs=-1, required=False)
@click.option("--update", "-u", is_flag=True, help="Update the lock file.")
@click.option(
    "--no-lock-dependencies",
    is_flag=True,
    help="Skip locking dependencies, only lock plugin definition.",
)
@click.pass_context
@pass_project()
def lock(
    project: Project,
    ctx: click.Context,
    *,
    all_plugins: bool,
    plugin_type: PluginType | None,
    plugin_name: tuple[str, ...],
    update: bool,
    no_lock_dependencies: bool,
) -> None:
    """Lock plugin definitions.

    \b
    Read more at https://docs.meltano.com/reference/command-line-interface#lock
    """  # noqa: D301
    tracker: Tracker = ctx.obj["tracker"]

    if all_plugins:
        warnings.warn(
            "The --all flag is deprecated and is no longer needed",
            DeprecationWarning,
            stacklevel=0,
        )

    lock_service = PluginLockService(project)

    try:
        with project.plugins.use_preferred_source(DefinitionSource.ANY):
            # Make it a list so source preference is not lazily evaluated.
            plugins = list(project.plugins.plugins())
    except Exception:
        tracker.track_command_event(CliEvent.aborted)
        raise

    if plugin_name:
        plugins = [plugin for plugin in plugins if plugin.name in plugin_name]

    if plugin_type is not None:
        plugins = [plugin for plugin in plugins if plugin.type == plugin_type]

    tracked_plugins: list[tuple[ProjectPlugin, str | None]] = []

    if not plugins:
        tracker.track_command_event(CliEvent.aborted)
        errmsg = "No matching plugin(s) found"
        raise CliError(errmsg)

    should_lock_deps = not no_lock_dependencies

    click.echo(f"Locking {len(plugins)} plugin(s)...")
    for plugin in plugins:
        descriptor = f"{plugin.type.descriptor} {plugin.name}"

        # Check if this is a custom or inherited plugin
        is_custom = plugin.is_custom()
        is_inherited = plugin.inherit_from is not None
        has_custom_pip_url = plugin.is_attr_set("pip_url")

        # Skip inherited plugins without custom pip_url - they use parent's lock
        if is_inherited and not has_custom_pip_url:
            click.secho(
                f"{descriptor.capitalize()} is an inherited plugin without custom pip_url",
                fg="yellow",
            )
            continue

        # Ensure plugin has parent (unless it's custom)
        if not is_custom:
            plugin.parent = None
            with project.plugins.use_preferred_source(DefinitionSource.HUB):
                plugin = project.plugins.ensure_parent(plugin)

        plugin_lock = PluginLock(project, plugin)

        # For custom or inherited plugins with custom pip_url: only lock dependencies
        if is_custom or (is_inherited and has_custom_pip_url):
            if should_lock_deps and has_custom_pip_url:
                try:
                    plugin_lock.save_dependencies(plugin.pip_url)
                    tracked_plugins.append((plugin, None))
                    click.secho(
                        f"Locked dependencies for {descriptor}",
                        fg="green",
                    )
                except Exception as err:
                    click.secho(
                        f"Failed to lock dependencies for {descriptor}: {err}",
                        fg="red",
                    )
            elif not has_custom_pip_url:
                click.secho(
                    f"Skipping {descriptor} - no pip_url to lock",
                    fg="yellow",
                )
            else:
                click.secho(
                    f"Skipping dependency lock for {descriptor} (--no-lock-dependencies)",
                    fg="yellow",
                )
        # For non-inherited, non-custom plugins: lock definition and optionally dependencies
        else:
            try:
                if plugin_lock.path.exists() and not update:
                    raise LockfileAlreadyExistsError(
                        f"Lockfile already exists: {plugin_lock.path}",  # noqa: EM102
                        plugin_lock.path,
                        plugin,
                    )
                plugin_lock.save(lock_dependencies=should_lock_deps)
                tracked_plugins.append((plugin, None))
                click.secho(f"Locked definition for {descriptor}", fg="green")
            except LockfileAlreadyExistsError as err:
                relative_path = err.path.relative_to(project.root)
                click.secho(
                    f"Lockfile exists for {descriptor} at {relative_path}",
                    fg="red",
                )
                continue

            # Show locked dependencies count if available
            if should_lock_deps and hasattr(plugin_lock, "variant"):
                variant = plugin_lock.variant
                if hasattr(variant, "pylock") and variant.pylock:
                    pkg_count = len(variant.pylock.get("packages", []))
                    click.secho(f"  └─ Locked {pkg_count} dependencies", fg="green")

    tracker.add_contexts(PluginsTrackingContext(tracked_plugins))
    tracker.track_command_event(CliEvent.completed)
