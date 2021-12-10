"""meltano run command and supporting functions."""
from typing import List, Union

import click
import structlog
from meltano.core.block.blockset import BlockSet
from meltano.core.block.extract_load import ExtractLoadBlocks
from meltano.core.block.parser import BlockParser, validate_block_sets
from meltano.core.block.plugin_command import InvokerCommand, PluginCommandBlock
from meltano.core.db import project_engine
from meltano.core.runner import RunnerError
from meltano.core.utils import click_run_async
from sqlalchemy.orm import Session

from . import CliError, cli
from .params import pass_project

logger = structlog.getLogger(__name__)


@cli.command(help="Like elt, with magic <preview feature>")
@click.argument(
    "blocks",
    nargs=-1,
)
@pass_project(migrate=True)
@click_run_async
async def run(project, blocks):
    """Run a set of blocks.

    Blocks are specified as a list of plugin names, e.g.
    `meltano run some_extractor some_loader some_plugin:some_command`.
    Blocks are run in the order they are specified from left to right.
    """
    if project.active_environment is None:
        logger.warning("No active environment, will run without job_id!")

    _, session_maker = project_engine(project)
    session = session_maker()

    try:  # noqa: WPS229
        parser = BlockParser(logger, project, blocks, session)
        parsed_blocks = list(parser.find_blocks(0))
        if not parsed_blocks:
            logger.info("No valid blocks found.")
            return
        if validate_block_sets(logger, parsed_blocks):
            logger.debug("All ExtractLoadBlocks validated, starting execution.")
        else:
            raise CliError("Some ExtractLoadBlocks set failed validation.")
        await _run_blocks(parsed_blocks, session)
    finally:
        session.close()


async def _run_single_block(blk: Union[BlockSet, PluginCommandBlock], session: Session):
    """Run a single block."""
    if isinstance(blk, ExtractLoadBlocks):
        await blk.run(session)
    elif isinstance(blk, InvokerCommand):
        await blk.run()
    else:
        raise Exception("Unknown block type.")


async def _run_blocks(
    parsed_blocks: List[Union[BlockSet, PluginCommandBlock]], session: Session
):
    for idx, blk in enumerate(parsed_blocks):
        try:
            await _run_single_block(blk, session)
        except RunnerError as err:
            logger.error(
                "Block run completed.",
                set_number=idx,
                block_type=blk.__class__.__name__,
                success=False,
                err=err,
                exit_codes=err.exitcodes,
            )
            raise CliError(
                f"Run invocation could not be completed as block failed: {err}"
            ) from err
        logger.info(
            "Block run completed.",
            set_number=idx,
            block_type=blk.__class__.__name__,
            success=True,
            err=None,
        )
