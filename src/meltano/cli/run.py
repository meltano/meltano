"""meltano run command and supporting functions."""
from typing import List, Union

import click
import structlog
from meltano.core.block.blockset import BlockSet
from meltano.core.block.parser import BlockParser, validate_block_sets
from meltano.core.block.plugin_command import PluginCommandBlock
from meltano.core.db import project_engine
from meltano.core.runner import RunnerError
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.utils import click_run_async
from sqlalchemy.orm import Session

from . import CliError, cli
from .params import pass_project

logger = structlog.getLogger(__name__)


@cli.command(short_help="[preview] Run a set of plugins in series.")
@click.argument(
    "blocks",
    nargs=-1,
)
@pass_project(migrate=True)
@click_run_async
async def run(project, blocks):
    """
    Run a set of command blocks in series.

    Blocks are specified as a list of plugin names, e.g.
    `meltano run some_extractor some_loader some_plugin:some_command` and are run in the order they are specified
    from left to right. A failure in any block will cause the entire run to abort.

    Multiple commmand blocks can be chained together or repeated, and tap/target pairs will automatically be linked:

        `meltano run tap-gitlab target-postgres dbt:test dbt:run`\n
        `meltano run tap-gitlab target-postgres tap-salesforce target-mysql ...`\n
        `meltano run tap-gitlab target-postgres dbt:run tap-postgres target-bigquery ...`\n

    This a preview feature - its functionality and cli signature is still evolving.

    \b\nRead more at https://meltano.com/docs/command-line-interface.html#run
    """
    if project.active_environment is not None:
        logger.warning("Job ID generation not yet supported - running without job!")

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

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_run(blocks)


async def _run_blocks(
    parsed_blocks: List[Union[BlockSet, PluginCommandBlock]], session: Session
) -> None:
    for idx, blk in enumerate(parsed_blocks):
        try:
            await blk.run(session)
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
