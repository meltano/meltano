"""Meltano run command and supporting functions."""

from __future__ import annotations

import typing as t

import click
import structlog

from meltano.cli.params import pass_project
from meltano.cli.utils import CliEnvironmentBehavior, CliError, PartialInstrumentedCmd
from meltano.core.block.blockset import BlockSet
from meltano.core.block.parser import BlockParser, validate_block_sets
from meltano.core.block.plugin_command import PluginCommandBlock
from meltano.core.logging.utils import change_console_log_level
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.runner import RunnerError
from meltano.core.tracking import BlockEvents, Tracker
from meltano.core.tracking.contexts import CliEvent
from meltano.core.tracking.contexts.plugins import PluginsTrackingContext
from meltano.core.utils import run_async

if t.TYPE_CHECKING:
    from meltano.core.project import Project

logger = structlog.getLogger(__name__)


@click.command(
    cls=PartialInstrumentedCmd,
    short_help="Run a set of plugins in series.",
    environment_behavior=CliEnvironmentBehavior.environment_required,
)
@click.option(
    "--dry-run",
    help=(
        "Do not run, just parse the invocation, validate it, and explain what "
        "would be executed."
    ),
    is_flag=True,
)
@click.option(
    "--full-refresh",
    help=(
        "Perform a full refresh (ignore state left behind by any previous "
        "runs). Applies to all pipelines."
    ),
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
    help=(
        "Force a new run even if a pipeline with the same State ID is already "
        "present. Applies to all pipelines."
    ),
    is_flag=True,
)
@click.option(
    "--state-id-suffix",
    help="Define a custom suffix to autogenerate state IDs with.",
)
@click.option(
    "--merge-state",
    is_flag=True,
    help="Merges state with that of previous runs.",
)
@click.argument(
    "blocks",
    nargs=-1,
)
@pass_project(migrate=True)
@click.pass_context
@run_async
async def run(
    ctx: click.Context,
    project: Project,
    dry_run: bool,
    full_refresh: bool,
    no_state_update: bool,
    force: bool,
    state_id_suffix: str,
    merge_state: bool,
    blocks: list[str],
):
    """
    Run a set of command blocks in series.

    Blocks are specified as either:\n
      - a list of plugin names\n
      - a job name\n
    An example of a list of plugin names is: `meltano run some_extractor some_loader some_plugin:some_optional_command`. These would be run in the order they are specified from left to right. A failure in any block will cause the entire run to abort.

    Multiple command blocks can be chained together or repeated, and tap/target pairs will automatically be linked:

        `meltano run tap-gitlab target-postgres dbt:test dbt:run`\n
        `meltano run tap-gitlab target-postgres tap-salesforce target-mysql ...`\n
        `meltano run tap-gitlab target-postgres dbt:run tap-postgres target-bigquery ...`\n

    When running within an active environment, meltano run activates incremental job support. State ID's are autogenerated
    using the format `{environment.name}:{extractor_name}-to-{loader_name}(:{state-id-suffix})` for each extract/load pair found:

        `meltano --environment=prod run tap-gitlab target-postgres tap-salesforce target-mysql`\n

    The above command will create two jobs with state IDs `prod:tap-gitlab-to-target-postgres` and `prod:tap-salesforce-to-target-mysql`.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#run
    """  # noqa: E501
    if dry_run and not ProjectSettingsService.config_override.get("cli.log_level"):
        logger.info("Setting 'console' handler log level to 'debug' for dry run")
        change_console_log_level()

    tracker: Tracker = ctx.obj["tracker"]

    try:
        parser = BlockParser(
            logger,
            project,
            blocks,
            full_refresh=full_refresh,
            no_state_update=no_state_update,
            force=force,
            state_id_suffix=state_id_suffix,
            merge_state=merge_state,
        )
        parsed_blocks = list(parser.find_blocks(0))
        if not parsed_blocks:
            tracker.track_command_event(CliEvent.aborted)
            logger.info("No valid blocks found.")
            return
    except Exception as parser_err:
        tracker.track_command_event(CliEvent.aborted)
        raise parser_err

    if validate_block_sets(logger, parsed_blocks):
        logger.debug("All ExtractLoadBlocks validated, starting execution.")
    else:
        tracker.track_command_event(CliEvent.aborted)
        raise CliError("Some ExtractLoadBlocks set failed validation.")  # noqa: EM101
    try:
        await _run_blocks(tracker, parsed_blocks, dry_run=dry_run)
    except Exception as err:
        tracker.track_command_event(CliEvent.failed)
        raise err
    tracker.track_command_event(CliEvent.completed)


async def _run_blocks(
    tracker: Tracker,
    parsed_blocks: list[BlockSet | PluginCommandBlock],
    dry_run: bool,
) -> None:
    for idx, blk in enumerate(parsed_blocks):
        blk_name = blk.__class__.__name__
        tracking_ctx = PluginsTrackingContext.from_block(blk)
        with tracker.with_contexts(tracking_ctx):
            tracker.track_block_event(blk_name, BlockEvents.initialized)
        if dry_run:
            msg = f"Dry run, but would have run block {idx + 1}/{len(parsed_blocks)}."
            if isinstance(blk, BlockSet):
                logger.info(
                    msg,
                    block_type=blk_name,
                    comprised_of=[plugin.string_id for plugin in blk.blocks],
                )
            elif isinstance(blk, PluginCommandBlock):
                logger.info(
                    msg,
                    block_type=blk_name,
                    comprised_of=f"{blk.string_id}:{blk.command}",
                )
            continue

        try:
            await blk.run()
        except RunnerError as err:
            logger.error(
                "Block run completed.",
                set_number=idx,
                block_type=blk_name,
                success=False,
                err=err,
                exit_codes=err.exitcodes,
            )
            with tracker.with_contexts(tracking_ctx):
                tracker.track_block_event(blk_name, BlockEvents.failed)
            raise CliError(
                f"Run invocation could not be completed as block failed: {err}",  # noqa: EM102
            ) from err
        except Exception as bare_err:
            # make sure we also fire block failed events for all other exceptions
            with tracker.with_contexts(tracking_ctx):
                tracker.track_block_event(blk_name, BlockEvents.failed)
            raise bare_err

        logger.info(
            "Block run completed.",
            set_number=idx,
            block_type=blk.__class__.__name__,
            success=True,
            err=None,
        )
        with tracker.with_contexts(tracking_ctx):
            tracker.track_block_event(blk_name, BlockEvents.completed)
