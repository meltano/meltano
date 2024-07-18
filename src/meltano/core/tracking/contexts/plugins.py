"""Tracking plugin context for the Snowplow tracker."""

from __future__ import annotations

import typing as t
import uuid

import structlog

from meltano._vendor.snowplow_tracker import SelfDescribingJson  # noqa: WPS436
from meltano.core.block.blockset import BlockSet
from meltano.core.block.plugin_command import PluginCommandBlock
from meltano.core.tracking.schemas import PluginsContextSchema
from meltano.core.utils import hash_sha256, safe_hasattr

if t.TYPE_CHECKING:
    from meltano.core.elt_context import ELTContext
    from meltano.core.plugin.project_plugin import ProjectPlugin

logger = structlog.stdlib.get_logger(__name__)


def _from_plugin(plugin: ProjectPlugin, cmd: str | None) -> dict:
    if not plugin or not safe_hasattr(plugin, "info"):
        # Don't try to snag any info for this plugin, we're somehow badly
        # malformed (unittest?), or where passed None. This event will be
        # routed to the "bad" bucket on the snowplow side. That makes it
        # detectable on our end, unlike if we had just filtered it out
        # completely.
        logger.debug(
            "Plugin tracker context some how encountered plugin without info attr.",
        )
        return {}

    return {
        "category": str(plugin.type),
        "name_hash": hash_sha256(plugin.name) if plugin.name else None,
        "namespace_hash": hash_sha256(plugin.namespace) if plugin.namespace else None,
        "executable_hash": hash_sha256(plugin.executable)
        if plugin.executable
        else None,
        "variant_name_hash": hash_sha256(plugin.variant) if plugin.variant else None,
        "pip_url_hash": hash_sha256(plugin.pip_url) if plugin.pip_url else None,
        "parent_name_hash": hash_sha256(plugin.parent.name) if plugin.parent else None,
        "command": cmd,
    }


# Proactively named to avoid name collisions more widely used "PluginContext"
class PluginsTrackingContext(SelfDescribingJson):
    """Tracking context for the Meltano plugins."""

    def __init__(self, plugins: list(tuple[ProjectPlugin, str | None])):
        """Initialize a meltano tracking plugin context.

        Args:
            plugins: The Meltano plugins and the requested command.
        """
        super().__init__(
            PluginsContextSchema.url,
            {
                "context_uuid": str(uuid.uuid4()),
                "plugins": [_from_plugin(plugin, cmd) for plugin, cmd in plugins],
            },
        )

    @classmethod
    def from_elt_context(cls, elt_context: ELTContext) -> PluginsTrackingContext:
        """Create a PluginsTrackingContext from an ELTContext.

        Args:
            elt_context: The ELTContext to use.

        Returns:
            A PluginsTrackingContext.
        """
        plugins = []
        if not elt_context.only_transform:
            plugins.extend(
                (
                    (elt_context.extractor.plugin, None),
                    (elt_context.loader.plugin, None),
                ),
            )
        if elt_context.transformer:
            plugins.append((elt_context.transformer.plugin, None))
        return cls(plugins)

    @classmethod
    def from_block(cls, blk: BlockSet | PluginCommandBlock) -> PluginsTrackingContext:
        """Create a PluginsTrackingContext from a BlockSet or PluginCommandBlock.

        Args:
            blk: The block to create the context for.

        Raises:
            TypeError: `blk` is not a `BlockSet` or `PluginCommandBlock`.

        Returns:
            The PluginsTrackingContext for the given block.
        """
        if isinstance(blk, BlockSet):
            plugins: list[tuple[ProjectPlugin, str]] = [
                (plugin_block.context.plugin, plugin_block.plugin_args)
                for plugin_block in blk.blocks
            ]

            return cls(plugins)
        if isinstance(blk, PluginCommandBlock):
            return cls([(blk.context.plugin, blk.command)])
        raise TypeError(
            "Parameter 'blk' must be an instance of 'BlockSet' or "  # noqa: EM102
            f"'PluginCommandBlock', not {type(blk)!r}",
        )

    @classmethod
    def from_blocks(
        cls,
        parsed_blocks: list[BlockSet | PluginCommandBlock],
    ) -> PluginsTrackingContext:
        """Create a `PluginsTrackingContext` from blocks.

        Args:
            parsed_blocks: The blocks to create the context from.

        Returns:
            The `PluginsTrackingContext` for the given blocks.
        """
        plugins: list[tuple[ProjectPlugin, str]] = []
        for blk in parsed_blocks:
            if isinstance(blk, BlockSet):
                plugins.extend(
                    (plugin_block.context.plugin, plugin_block.plugin_args)
                    for plugin_block in blk.blocks
                )
            elif isinstance(blk, PluginCommandBlock):
                plugins.append((blk.context.plugin, blk.command))
        return PluginsTrackingContext(plugins)
