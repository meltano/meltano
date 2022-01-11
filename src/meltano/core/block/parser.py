"""Utilities for turning a string list of plugins into a usable list of BlockSet and PluginCommand objects."""
from typing import Generator, List, Tuple, Union

import click
import structlog
from meltano.core.block.blockset import BlockSet, BlockSetValidationError
from meltano.core.block.extract_load import ELBContextBuilder, ExtractLoadBlocks
from meltano.core.block.ioblock import IOBlock
from meltano.core.block.plugin_command import PluginCommandBlock, plugin_command_invoker
from meltano.core.block.singer import SingerBlock
from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService


def is_command_block(plugin: ProjectPlugin) -> bool:
    """Check if a plugin is a command block.

    Note: currently, our only command block is dbt so we just check if the plugin type is a TRANSFORMERS.

    Args:
        plugin: Plugin to check.
    Returns:
        True if plugin is a command block.
    """
    return plugin.type not in {PluginType.EXTRACTORS, PluginType.LOADERS}


def generate_job_id(
    project: Project, consumer: IOBlock, producer: IOBlock
) -> Union[str, None]:
    """Generate a job id based on a project active environment and consumer and producer names.

    Args:
        project: Project to retrieve active environment from.
        consumer: Consumer block.
        producer: Producer block.
    Returns:
        Job id or None if project active environment is not set.
    """
    if project.active_environment:
        return f"{project.active_environment.name}-{consumer.string_id}-{producer.string_id}"
    return None


def validate_block_sets(
    log: structlog.BoundLogger, blocks: List[Union[BlockSet, PluginCommandBlock]]
) -> bool:
    """Perform validation of a all blocks in a list that implement the BlockSet interface.

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
        session=None,
    ):
        """
        Parse a meltano run command invocation into a list of blocks.

        Args:
            log: Logger to use.
            project: Project to use.
            blocks: List of block names to parse.
            session: Optional session to use.
        """
        self.log = log
        self.blocks = blocks
        self.project = project
        self.session = session

        self._plugins_service = ProjectPluginsService(project)
        self._plugins: List[ProjectPlugin] = []

        self._commands: dict[ProjectPlugin, str] = {}

        for name in blocks:

            try:
                parsed_name, command_name = name.split(":")
            except ValueError:
                parsed_name = name
                command_name = None

            plugin = self._plugins_service.find_plugin(parsed_name)
            if plugin is None:
                raise click.ClickException(f"Block {name} not found")
            self._plugins.append(plugin)
            if command_name:
                self._commands[plugin] = command_name
            self.log.debug("found plugin in cli invocation", plugin_name=plugin.name)

    def find_blocks(
        self, offset: int = 0
    ) -> Generator[Union[BlockSet, PluginCommandBlock], None, None]:
        """
        Find all blocks in the invocation.

        Args:
            offset: Offset to start from.

        Returns:
            Generator of blocks (either BlockSet or PluginCommandBlock).
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
                    session=self.session,
                    command=self._commands.get(plugin),
                )
                cur += 1
            else:
                raise Exception(
                    f"Unknown command type or bad block sequence at index {cur + 1}, starting block '{plugin.name}'"
                )

    def _find_next_elb_set(  # noqa: WPS231
        self,
        offset: int = 0,
    ) -> Tuple[ExtractLoadBlocks, int]:  # noqa: WPS231
        """
        Search a list of project plugins trying to find an extract ExtractLoad block set.

        Args:
            plugins: List of project plugins to search.
            offset: Optional starting offset for search.
        Returns:
            The ExtractLoad object.
            Offset for remaining plugins.
        """
        blocks: List[SingerBlock] = []

        builder = ELBContextBuilder(self.project, self._plugins_service, self.session)

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
            if plugin.type != PluginType.LOADERS:
                self.log.debug(
                    "next block not loader",
                    offset=offset,
                    plugin_type=plugin.type,
                )
                return None, offset + idx + 1

            self.log.debug("found block", block_type=plugin.type, index=idx + 1)
            if plugin.type == PluginType.TRANSFORMS or PluginType.LOADERS:
                blocks.append(builder.make_block(plugin))
                if plugin.type == PluginType.LOADERS:
                    self.log.debug("blocks", offset=offset, idx=idx + 1)
                    elb = ExtractLoadBlocks(builder.context(), blocks)
                    return elb, idx + 2
            else:
                self.log.warning(
                    "Found unexpected plugin type for block in middle of block set.",
                    plugin_type=plugin.type,
                    plugin_name=plugin.name,
                )
                raise BlockSetValidationError(
                    f"Expected {PluginType.TRANSFORMS} or {PluginType.LOADERS}."
                )
        raise Exception("Found no end in block set!")
