"""Lock command."""

from __future__ import annotations

import typing as t
from dataclasses import dataclass

import click
import structlog

from meltano.cli.params import PluginTypeArg, pass_project
from meltano.cli.utils import CliError, PartialInstrumentedCmd
from meltano.core.plugin_lock_service import PluginLock
from meltano.core.project_plugins_service import DefinitionSource
from meltano.core.tracking.contexts import CliEvent, PluginsTrackingContext

if t.TYPE_CHECKING:
    from meltano.core.plugin import PluginType
    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project
    from meltano.core.tracking import Tracker


__all__ = ["lock"]
logger = structlog.get_logger(__name__)


@dataclass
class LockStrategy:
    """Strategy for locking a plugin."""

    skip: bool = False
    lock_definition: bool = False
    lock_dependencies: bool = False
    pip_url: str | None = None
    message: str = ""


def _determine_lock_strategy(
    plugin: ProjectPlugin,
    *,
    should_lock_deps: bool,
) -> LockStrategy:
    """Determine what should be locked for this plugin.

    Args:
        plugin: The plugin to determine strategy for.
        should_lock_deps: Whether dependencies should be locked.

    Returns:
        LockStrategy indicating what to lock and any skip message.
    """
    is_custom = plugin.is_custom()
    is_inherited = plugin.inherit_from is not None
    has_custom_pip_url = plugin.is_attr_set("pip_url")
    descriptor = f"{plugin.type.descriptor} {plugin.name}"

    # Skip inherited plugins without custom pip_url - they use parent's lock
    if is_inherited and not has_custom_pip_url:
        return LockStrategy(
            skip=True,
            message=(
                f"{descriptor.capitalize()} is an inherited plugin "
                "without custom pip_url"
            ),
        )

    # Custom or inherited with custom pip_url: only lock dependencies
    if is_custom or (is_inherited and has_custom_pip_url):
        if not has_custom_pip_url:
            return LockStrategy(
                skip=True,
                message=f"Skipping {descriptor} - no pip_url to lock",
            )
        if not should_lock_deps:
            return LockStrategy(
                skip=True,
                message=(
                    f"Skipping dependency lock for {descriptor} "
                    "(--no-lock-dependencies)"
                ),
            )
        return LockStrategy(
            lock_dependencies=True,
            pip_url=plugin.pip_url,
        )

    # Standard plugins: lock definition and optionally dependencies
    return LockStrategy(
        lock_definition=True,
        lock_dependencies=should_lock_deps,
    )


@click.command(cls=PartialInstrumentedCmd, short_help="Lock plugin definitions.")
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

    logger.info("Locking %d plugin(s)", len(plugins))
    for plugin in plugins:
        descriptor = f"{plugin.type.descriptor} {plugin.name}"

        # Determine lock strategy for this plugin
        strategy = _determine_lock_strategy(plugin, should_lock_deps=should_lock_deps)

        # Skip if strategy says so
        if strategy.skip:
            logger.info(strategy.message)
            continue

        # Ensure plugin has parent (unless it's custom)
        if not plugin.is_custom():
            plugin.parent = None
            with project.plugins.use_preferred_source(DefinitionSource.HUB):
                plugin = project.plugins.ensure_parent(plugin)

        plugin_lock = PluginLock(project, plugin)

        # Execute the locking operations
        try:
            # Lock definition if needed
            if strategy.lock_definition:
                if plugin_lock.path.exists() and not update:
                    relative_path = plugin_lock.path.relative_to(project.root)
                    logger.warning(
                        "Lockfile exists for %s at %s",
                        descriptor,
                        relative_path,
                    )
                else:
                    plugin_lock.save_definition()
                    logger.info("Locked definition for %s", descriptor)

            # Lock dependencies if needed
            if strategy.lock_dependencies:
                # Get pip_url from strategy or from saved definition
                pip_url = strategy.pip_url
                if not pip_url and hasattr(plugin_lock, "variant"):
                    from meltano.core.plugin.base import StandalonePlugin

                    locked_def = StandalonePlugin.from_variant(
                        plugin_lock.variant,
                        plugin_lock.definition,
                    )
                    pip_url = locked_def.pip_url

                if pip_url:
                    if plugin_lock.pylock_path.exists() and not update:
                        relative_path = plugin_lock.pylock_path.relative_to(
                            project.root,
                        )
                        logger.warning(
                            "Pylock exists for %s at %s",
                            descriptor,
                            relative_path,
                        )
                    else:
                        plugin_lock.save_dependencies(pip_url)

            tracked_plugins.append((plugin, None))

        except Exception as err:
            logger.exception("Failed to lock %s: %s", descriptor, err)
            continue

    tracker.add_contexts(PluginsTrackingContext(tracked_plugins))
    tracker.track_command_event(CliEvent.completed)
