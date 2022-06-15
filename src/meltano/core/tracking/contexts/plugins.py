"""Tracking plugin context for the Snowplow tracker."""
from __future__ import annotations

import uuid

from snowplow_tracker import SelfDescribingJson
from structlog.stdlib import get_logger

from meltano.core.block.blockset import BlockSet
from meltano.core.block.plugin_command import PluginCommandBlock
from meltano.core.elt_context import ELTContext
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.tracking.schemas import PluginsContextSchema
from meltano.core.utils import hash_sha256, safe_hasattr

logger = get_logger(__name__)


def _from_plugin(plugin: ProjectPlugin, cmd: str) -> dict:
    if not safe_hasattr(plugin, "info"):
        logger.debug(
            "Plugin tracker context some how encountered plugin without info attr."
        )
        # don't try to snag any info for this plugin, we're somehow badly malformed (unittest?)
        return {}

    return {
        "category": str(plugin.type),
        "name_hash": hash_sha256(plugin.name) if plugin.name else None,
        "namespace_hash": hash_sha256(plugin.namespace) if plugin.namespace else None,
        "executable_hash": hash_sha256(plugin.executable)
        if plugin.executable
        else None,
        "variant_name_hash": hash_sha256(plugin.variant) if plugin.variant else None,
        "pip_url_hash": hash_sha256(plugin.formatted_pip_url)
        if plugin.formatted_pip_url
        else None,
        "parent_name_hash": hash_sha256(plugin.parent.name)
        if plugin.parent.name
        else None,
        "command": cmd,
    }


# Proactively named to avoid name collisions more widely used "PluginContext"
class PluginsTrackingContext(SelfDescribingJson):
    """Tracking context for the Meltano plugins."""

    def __init__(self, plugins: list(tuple[ProjectPlugin, str])):
        """Initialize a meltano tracking plugin context.

        Args:
            plugins: The Meltano plugins and the requested command.
        """
        tracking_context = []
        for plugin, cmd in plugins:
            tracking_context.append(_from_plugin(plugin, cmd))

        super().__init__(
            PluginsContextSchema.url,
            {"context_uuid": str(uuid.uuid4()), "plugins": tracking_context},
        )

    def append_plugin_context(self, plugin: ProjectPlugin, cmd: str):
        """Append a plugin context to the tracking context.

        Args:
            plugin: The Meltano plugin.
            cmd: The command that was executed.
        """
        self["plugins"].append({_from_plugin(plugin, cmd)})

    @classmethod
    def from_elt_context(cls, elt_context: ELTContext) -> PluginsTrackingContext:
        """Create a PluginsTrackingContext from an ELTContext.

        Parameters:
            elt_context: The ELTContext to use.

        Returns:
            A PluginsTrackingContext.
        """
        plugins = []
        if not elt_context.only_transform:
            plugins.append((elt_context.extractor.plugin, None))
            plugins.append((elt_context.loader.plugin, None))
        if elt_context.transformer:
            plugins.append((elt_context.transformer.plugin, None))
        return cls(plugins)

    @classmethod
    def from_block(cls, blk: BlockSet | PluginCommandBlock) -> PluginsTrackingContext:
        """Create a PluginsTrackingContext from a BlockSet or PluginCommandBlock.

        Parameters:
            blk: The block to create the context for.

        Raises:
            TypeError: `blk` is not a `BlockSet` or `PluginCommandBlock`.

        Returns:
            The PluginsTrackingContext for the given block.
        """
        if isinstance(blk, BlockSet):
            plugins: list[(ProjectPlugin, str)] = []
            for plugin_block in blk.blocks:
                plugins.append((plugin_block.context.plugin, plugin_block.plugin_args))
            return cls(plugins)
        if isinstance(blk, PluginCommandBlock):
            return cls([(blk.context.plugin, blk.command)])
        raise TypeError(
            "Parameter 'blk' must be an instance of 'BlockSet' or 'PluginCommandBlock', "
            + f"not {type(blk)!r}"
        )
