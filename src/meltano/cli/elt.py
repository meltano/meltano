"""Defines `meltano elt` command."""

import datetime
import logging
from contextlib import contextmanager

import click
from async_generator import asynccontextmanager
from structlog import stdlib as structlog_stdlib

from meltano.core.db import project_engine
from meltano.core.elt_context import ELTContextBuilder
from meltano.core.job import Job, JobFinder
from meltano.core.job.stale_job_failer import StaleJobFailer
from meltano.core.legacy_tracking import LegacyTracker
from meltano.core.logging import JobLoggingService, OutputLogger
from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.runner import RunnerError
from meltano.core.runner.dbt import DbtRunner
from meltano.core.runner.singer import SingerRunner
from meltano.core.utils import click_run_async

from . import cli
from .params import pass_project
from .utils import CliError

DUMPABLES = {
    "catalog": (PluginType.EXTRACTORS, "catalog"),
    "state": (PluginType.EXTRACTORS, "state"),
    "extractor-config": (PluginType.EXTRACTORS, "config"),
    "loader-config": (PluginType.LOADERS, "config"),
}

logger = structlog_stdlib.get_logger(__name__)


@cli.command(short_help="Run an ELT pipeline to Extract, Load, and Transform data.")
@click.argument("extractor")
@click.argument("loader")
@click.option("--transform", type=click.Choice(["skip", "only", "run"]), default="skip")
@click.option("--dry", help="Do not actually run.", is_flag=True)
@click.option(
    "--full-refresh",
    help="Perform a full refresh (ignore state left behind by any previous runs).",
    is_flag=True,
)
@click.option(
    "--select",
    "-s",
    help="Select only these specific entities for extraction.",
    multiple=True,
    default=[],
)
@click.option(
    "--exclude",
    "-e",
    help="Exclude these specific entities from extraction.",
    multiple=True,
    default=[],
)
@click.option("--catalog", help="Extractor catalog file.")
@click.option("--state", help="Extractor state file.")
@click.option(
    "--dump",
    type=click.Choice(DUMPABLES.keys()),
    help="Dump content of pipeline-specific generated file.",
)
@click.option(
    "--state-id", envvar="MELTANO_STATE_ID", help="A custom string to identify the job."
)
@click.option(
    "--force",
    "-f",
    help="Force a new run even when a pipeline with the same state ID is already running.",
    is_flag=True,
)
@pass_project(migrate=True)
@click_run_async
async def elt(
    project,
    extractor,
    loader,
    transform,
    dry,
    full_refresh,
    select,
    exclude,
    catalog,
    state,
    dump,
    state_id,
    force,
):
    """
    Run an ELT pipeline to Extract, Load, and Transform data.

    meltano elt '<extractor_name>' '<loader_name>'

    extractor_name: extractor to be used in this pipeline.
    loader_name: loader to be used in this pipeline.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#elt
    """
    select_filter = [*select, *(f"!{entity}" for entity in exclude)]

    job = Job(
        job_id=state_id
        or f'{datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%S")}--{extractor}--{loader}'
    )

    _, Session = project_engine(project)  # noqa: N806
    session = Session()
    try:
        plugins_service = ProjectPluginsService(project)
        context_builder = _elt_context_builder(
            project,
            job,
            session,
            extractor,
            loader,
            transform,
            dry_run=dry,
            full_refresh=full_refresh,
            select_filter=select_filter,
            catalog=catalog,
            state=state,
            plugins_service=plugins_service,
        )

        if dump:
            await dump_file(context_builder, dump)
        else:
            await _run_job(project, job, session, context_builder, force=force)
    finally:
        session.close()

    tracker = LegacyTracker(project)
    tracker.track_meltano_elt(extractor=extractor, loader=loader, transform=transform)


def _elt_context_builder(
    project,
    job,
    session,
    extractor,
    loader,
    transform,
    dry_run=False,
    full_refresh=False,
    select_filter=None,
    catalog=None,
    state=None,
    plugins_service=None,
):
    select_filter = select_filter or []
    transform_name = None
    if transform != "skip":
        transform_name = _find_transform_for_extractor(
            extractor, plugins_service=plugins_service
        )

    return (
        ELTContextBuilder(project, plugins_service=plugins_service)  # noqa: WPS221
        .with_session(session)
        .with_job(job)
        .with_extractor(extractor)
        .with_loader(loader)
        .with_transform(transform_name or transform)
        .with_dry_run(dry_run)
        .with_only_transform(transform == "only")
        .with_full_refresh(full_refresh)
        .with_select_filter(select_filter)
        .with_catalog(catalog)
        .with_state(state)
    )


async def dump_file(context_builder, dumpable):
    """Dump the given dumpable for this pipeline."""
    elt_context = context_builder.context()

    try:
        plugin_type, file_id = DUMPABLES[dumpable]
        invoker = elt_context.invoker_for(plugin_type)

        async with invoker.prepared(elt_context.session):
            content = await invoker.dump(file_id)

        click.echo(content)
    except FileNotFoundError as err:
        raise CliError(f"Could not find {dumpable} file for this pipeline") from err
    except Exception as err:
        raise CliError(f"Could not dump {dumpable}: {err}") from err


async def _run_job(project, job, session, context_builder, force=False):
    StaleJobFailer(job.job_id).fail_stale_jobs(session)

    if not force:
        existing = JobFinder(job.job_id).latest_running(session)
        if existing:
            raise CliError(
                f"Another '{job.job_id}' pipeline is already running which started at {existing.started_at}. "
                + "To ignore this check use the '--force' option."
            )

    async with job.run(session):
        job_logging_service = JobLoggingService(project)
        log_file = job_logging_service.generate_log_name(job.job_id, job.run_id)

        output_logger = OutputLogger(log_file)
        context_builder.set_base_output_logger(output_logger)

        log = logger.bind(name="meltano", run_id=str(job.run_id), state_id=job.job_id)

        await _run_elt(log, context_builder, output_logger)


@asynccontextmanager
async def _redirect_output(log, output_logger):

    meltano_stdout = output_logger.out(
        "meltano", log.bind(stdio="stdout", cmd_type="elt")
    )
    meltano_stderr = output_logger.out(
        "meltano", log.bind(stdio="stderr", cmd_type="elt")
    )

    with meltano_stdout.redirect_logging(ignore_errors=(CliError,)):
        async with meltano_stdout.redirect_stdout(), meltano_stderr.redirect_stderr():  # noqa: WPS316
            try:
                yield
            except CliError as err:
                err.print()
                raise


async def _run_elt(log, context_builder, output_logger):
    async with _redirect_output(log, output_logger):
        try:
            elt_context = context_builder.context()

            if elt_context.only_transform:
                log.info("Extract & load skipped.")
            else:
                await _run_extract_load(log, elt_context, output_logger)

            if elt_context.transformer:
                await _run_transform(log, elt_context, output_logger)
            else:
                log.info("Transformation skipped.")
        except RunnerError as err:
            raise CliError(
                f"ELT could not be completed: {err}.\n"
                + "For more detailed log messages re-run the command using 'meltano --log-level=debug ...' CLI flag.\n"
                + f"Note that you can also check the generated log file at '{output_logger.file}'.\n"
                + "For more information on debugging and logging: https://docs.meltano.com/reference/command-line-interface#debugging"
            ) from err


async def _run_extract_load(log, elt_context, output_logger, **kwargs):  # noqa: WPS231

    extractor = elt_context.extractor.name
    loader = elt_context.loader.name

    stderr_log = logger.bind(
        run_id=str(elt_context.job.run_id),
        state_id=elt_context.job.job_id,
        stdio="stderr",
    )

    extractor_log = output_logger.out(extractor, stderr_log.bind(cmd_type="extractor"))
    loader_log = output_logger.out(loader, stderr_log.bind(cmd_type="loader"))

    @contextmanager
    def nullcontext():
        yield None

    extractor_out_writer_ctxmgr = nullcontext
    loader_out_writer_ctxmgr = nullcontext
    if logger.getEffectiveLevel() == logging.DEBUG:
        stdout_log = logger.bind(
            run_id=str(elt_context.job.run_id),
            state_id=elt_context.job.job_id,
            stdio="stdout",
        )
        extractor_out = output_logger.out(
            f"{extractor} (out)", stdout_log.bind(cmd_type="extractor"), logging.DEBUG
        )
        loader_out = output_logger.out(
            f"{loader} (out)", stdout_log.bind(cmd_type="loader"), logging.DEBUG
        )

        extractor_out_writer_ctxmgr = extractor_out.line_writer
        loader_out_writer_ctxmgr = loader_out.line_writer

    log.info(
        "Running extract & load...",
    )

    singer_runner = SingerRunner(elt_context)
    try:
        with extractor_log.line_writer() as extractor_log_writer, loader_log.line_writer() as loader_log_writer:
            with extractor_out_writer_ctxmgr() as extractor_out_writer, loader_out_writer_ctxmgr() as loader_out_writer:
                await singer_runner.run(
                    **kwargs,
                    extractor_log=extractor_log_writer,
                    loader_log=loader_log_writer,
                    extractor_out=extractor_out_writer,
                    loader_out=loader_out_writer,
                )
    except RunnerError as err:
        try:  # noqa: WPS505
            code = err.exitcodes[PluginType.EXTRACTORS]
            message = extractor_log.last_line.rstrip() or "(see above)"
            log.error("Extraction failed", code=code, message=message)
        except KeyError:
            pass

        try:  # noqa: WPS505
            code = err.exitcodes[PluginType.LOADERS]
            message = loader_log.last_line.rstrip() or "(see above)"
            log.error("Loading failed", code=code, message=message)
        except KeyError:
            pass

        raise

    log.info("Extract & load complete!")


async def _run_transform(log, elt_context, output_logger, **kwargs):

    stderr_log = logger.bind(
        run_id=str(elt_context.job.run_id),
        state_id=elt_context.job.job_id,
        stdio="stderr",
        cmd_type="transformer",
    )

    transformer_log = output_logger.out(elt_context.transformer.name, stderr_log)

    log.info("Running transformation...")

    dbt_runner = DbtRunner(elt_context)
    try:
        with transformer_log.line_writer() as transformer_log_writer:
            await dbt_runner.run(**kwargs, log=transformer_log_writer)
    except RunnerError as err:
        try:  # noqa: WPS505
            code = err.exitcodes[PluginType.TRANSFORMERS]
            message = transformer_log.last_line.rstrip() or "(see above)"
            log.error("Transformation failed", code=code, message=message)
        except KeyError:
            pass

        raise

    log.info("Transformation complete!")


def _find_transform_for_extractor(extractor: str, plugins_service):
    discovery_service = plugins_service.discovery_service
    try:
        extractor_plugin_def = discovery_service.find_definition(
            PluginType.EXTRACTORS, extractor
        )

        # Check if there is a default transform for this extractor
        transform_plugin_def = discovery_service.find_definition_by_namespace(
            PluginType.TRANSFORMS, extractor_plugin_def.namespace
        )

        # Check if the transform has been added to the project
        transform_plugin = plugins_service.get_plugin(transform_plugin_def)

        return transform_plugin.name
    except PluginNotFoundError:
        return None
