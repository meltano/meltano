"""Utilities for turning a string list of plugins into a usable list of BlockSet and PluginCommand objects."""
from typing import Dict, Generator, List, Optional, Tuple, Union

import click
import structlog

from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.project_plugins_service import ProjectPluginsService

from .blockset import BlockSet, BlockSetValidationError
from .extract_load import ELBContextBuilder, ExtractLoadBlocks
from .plugin_command import PluginCommandBlock, plugin_command_invoker
from .singer import CONSUMERS, SingerBlock


def is_command_block(plugin: ProjectPlugin) -> bool:
    """Check if a plugin is a command block.

    Args:
        plugin: Plugin to check.

    Returns:
        True if plugin is a command block.
    """
    return plugin.type not in {
        PluginType.EXTRACTORS,
        PluginType.LOADERS,
        PluginType.MAPPERS,
    }


def validate_block_sets(
    log: structlog.BoundLogger, blocks: List[Union[BlockSet, PluginCommandBlock]]
) -> bool:
    """Perform validation of all blocks in a list that implement the BlockSet interface.

    Args:
        log: Logger to use in the event of a validation error.
        blocks: A list of blocks.

    Returns:
        True if all blocks are valid, False otherwise.
    """
    for idx, blk in enumerate(blocks):
        if blk == BlockSet:
            log.debug("validating ExtractLoadBlock.", set_number=idx)
            try:
                blk.validate_set()
            except Exception as err:
                log.error("Validation failed.", err=err)
                return False
    return True


class BlockParser:  # noqa: D101
    def __init__(
        self,
        log: structlog.BoundLogger,
        project,
        blocks: List[str],
        full_refresh: Optional[bool] = False,
        no_state_update: Optional[bool] = False,
        force: Optional[bool] = False,
    ):
        """
        Parse a meltano run command invocation into a list of blocks.

        Args:
            log: Logger to use.
            project: Project to use.
            blocks: List of block names to parse.
            full_refresh: Whether to perform a full refresh (applies to all found sets).
            no_state_update: Whether to run with or without state updates.
            force: Whether to force a run if a job is already running (applies to all found sets).

        Raises:
            ClickException: If a block name is not found.
        """
        self.log = log
        self.project = project

        self._full_refresh = full_refresh
        self._no_state_update = no_state_update
        self._force = force

        self._plugins_service = ProjectPluginsService(project)
        self._plugins: List[ProjectPlugin] = []

        self._commands: Dict[int, str] = {}
        self._mappings_ref: Dict[int, str] = {}

        for idx, name in enumerate(blocks):

            try:
                parsed_name, command_name = name.split(":")
            except ValueError:
                parsed_name = name
                command_name = None

            plugin = self._find_plugin_or_mapping(parsed_name)
            if plugin is None:
                raise click.ClickException(f"Block {name} not found")

            if plugin.type == PluginType.MAPPERS:
                self._mappings_ref[idx] = parsed_name

            self._plugins.append(plugin)
            if command_name:
                self._commands[idx] = command_name
                self.log.debug(
                    "plugin command added for execution",
                    commands=self._commands,
                    command_name=command_name,
                    plugin_name=parsed_name,
                )

            self.log.debug("found plugin in cli invocation", plugin_name=plugin.name)

        self.log.info("commands", commands=self._commands)

    def find_blocks(
        self, offset: int = 0
    ) -> Generator[Union[BlockSet, PluginCommandBlock], None, None]:
        """
        Find all blocks in the invocation.

        Args:
            offset: Offset to start from.

        Yields:
            Generator of blocks (either BlockSet or PluginCommandBlock).

        Raises:
            BlockSetValidationError: If unknown command is found or if a unexpected block sequence is found.
        """
        cur = offset
        while cur < len(self._plugins):
            plugin = self._plugins[cur]
            elb, idx = self._find_next_elb_set(cur)
            if elb:
                self.log.debug("found ExtractLoadBlocks set", offset=cur)
                yield elb
                cur += idx
            elif is_command_block(plugin):
                self.log.debug(
                    "found PluginCommand",
                    offset=cur,
                    plugin_type=plugin.type,
                )
                yield plugin_command_invoker(
                    self._plugins[cur],
                    self.project,
                    command=self._commands.get(cur),
                )
                cur += 1
            else:
                raise BlockSetValidationError(
                    f"Unknown command type or bad block sequence at index {cur + 1}, starting block '{plugin.name}'"  # noqa: WPS237
                )

    def _find_plugin_or_mapping(self, name: str) -> Optional[ProjectPlugin]:
        """Find a plugin by name OR by mapping name.

        Args:
            name: Name of the plugin or mapping.

        Returns:
            The actual plugin.

        Raises:
            ClickException: If mapping name returns multiple matches.
        """
        try:
            return self._plugins_service.find_plugin(name)
        except PluginNotFoundError:
            pass

        mapper = None
        try:
            mapper = self._plugins_service.find_plugins_by_mapping_name(name)
        except PluginNotFoundError:
            pass

        if mapper is None:
            return None

        if len(mapper) > 1:
            raise click.ClickException(
                f"Ambiguous mapping name {name}, found multiple matches."
            )
        return mapper[0] if mapper else None

    def _find_next_elb_set(  # noqa: WPS231, WPS213
        self,
        offset: int = 0,
    ) -> Tuple[Optional[ExtractLoadBlocks], int]:  # noqa: WPS231, WPS213
        """
        Search a list of project plugins trying to find an extract ExtractLoad block set.

        Args:
            offset: Optional starting offset for search.

        Returns:
            The ExtractLoad object.
            Offset for remaining plugins.

        Raises:
            BlockSetValidationError: If the block set is not valid.
        """
        blocks: List[SingerBlock] = []

        base_builder = ELBContextBuilder(
            self.project, self._plugins_service
        )  # lint work around
        builder = (
            base_builder.with_force(self._force)
            .with_full_refresh(self._full_refresh)
            .with_no_state_update(self._no_state_update)
        )

        if self._plugins[offset].type != PluginType.EXTRACTORS:
            self.log.debug(
                "next block not extractor",
                offset=offset,
                plugin_type=self._plugins[offset].type,
            )
            return None, offset

        self.log.debug(
            "head of set is extractor as expected", block=self._plugins[offset]
        )

        blocks.append(builder.make_block(self._plugins[offset]))

        for idx, plugin in enumerate(self._plugins[offset + 1 :]):  # noqa: E203
            next_block = idx + 1

            if plugin.type not in CONSUMERS:
                self.log.debug(
                    "next block not a consumer of output",
                    offset=offset,
                    plugin_type=plugin.type,
                )
                return None, offset + next_block

            self.log.debug("found block", block_type=plugin.type, index=next_block)

            if plugin.type == PluginType.MAPPERS:
                self.log.info(
                    "found mapper",
                    plugin_type=plugin.type,
                    plugin_name=plugin.name,
                    mapping=self._mappings_ref.get(next_block),
                    idx=next_block,
                )
                blocks.append(
                    builder.make_block(
                        plugin,
                    )
                )
            elif plugin.type == PluginType.LOADERS:
                self.log.debug("blocks", offset=offset, idx=next_block)
                blocks.append(builder.make_block(plugin))
                elb = ExtractLoadBlocks(builder.context(), blocks)
                return elb, idx + 2
            else:
                self.log.warning(
                    "Found unexpected plugin type for block in middle of block set.",
                    plugin_type=plugin.type,
                    plugin_name=plugin.name,
                )
                raise BlockSetValidationError(
                    f"Expected {PluginType.MAPPERS} or {PluginType.LOADERS}."
                )
        raise BlockSetValidationError("Found no end in block set!")
