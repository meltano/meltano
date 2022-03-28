"""meltano run command and supporting functions."""
from typing import List, Union

import click
import structlog

from meltano.core.block.blockset import BlockSet
from meltano.core.block.parser import BlockParser, validate_block_sets
from meltano.core.block.plugin_command import PluginCommandBlock
from meltano.core.project import Project
from meltano.core.runner import RunnerError
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.utils import click_run_async

from . import CliError, cli
from .params import pass_project

logger = structlog.getLogger(__name__)


@cli.command(short_help="[preview] Run a set of plugins in series.")
@click.option(
    "--full-refresh",
    help="Perform a full refresh (ignore state left behind by any previous runs). Applies to all pipelines.",
    is_flag=True,
)
@click.option(
    "--no-state-update",
    help="Run without state saving. Applies to all pipelines.",
    is_flag=True,
)
@click.option(
    "--force",
    "-f",
    help="Force a new run even if a pipeline with the same Job ID is already present. Applies to all pipelines.",
    is_flag=True,
)
@click.argument(
    "blocks",
    nargs=-1,
)
@pass_project(migrate=True)
@click_run_async
async def run(
    project: Project,
    full_refresh: bool,
    no_state_update: bool,
    force: bool,
    blocks: List[str],
):
    """
    Run a set of command blocks in series.

    Blocks are specified as a list of plugin names, e.g.
    `meltano run some_extractor some_loader some_plugin:some_command` and are run in the order they are specified
    from left to right. A failure in any block will cause the entire run to abort.

    Multiple commmand blocks can be chained together or repeated, and tap/target pairs will automatically be linked:

        `meltano run tap-gitlab target-postgres dbt:test dbt:run`\n
        `meltano run tap-gitlab target-postgres tap-salesforce target-mysql ...`\n
        `meltano run tap-gitlab target-postgres dbt:run tap-postgres target-bigquery ...`\n

    When running within an active environment, meltano run activates incremental job support. Job ID's are autogenerated
    using the format `{active_environment.name}:{extractor_name}-to-{loader_name}` for each extract/load pair found:

        `meltano --environment=prod run tap-gitlab target-postgres tap-salesforce target-mysql`\n

    The above command will create two jobs with the IDs `prod:tap-gitlab-to-target-postgres` and `prod:tap-salesforce-to-target-mysql`.

    This a preview feature - its functionality and cli signature is still evolving.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#run
    """
    parser = BlockParser(logger, project, blocks, full_refresh, no_state_update, force)
    parsed_blocks = list(parser.find_blocks(0))
    if not parsed_blocks:
        logger.info("No valid blocks found.")
        return
    if validate_block_sets(logger, parsed_blocks):
        logger.debug("All ExtractLoadBlocks validated, starting execution.")
    else:
        raise CliError("Some ExtractLoadBlocks set failed validation.")
    await _run_blocks(parsed_blocks)

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_run(blocks)


async def _run_blocks(parsed_blocks: List[Union[BlockSet, PluginCommandBlock]]) -> None:
    for idx, blk in enumerate(parsed_blocks):
        try:
            await blk.run()
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
