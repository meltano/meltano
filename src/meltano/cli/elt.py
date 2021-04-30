"""Defines `meltano elt` command."""
import datetime
import logging
import os
import sys
from contextlib import contextmanager

import click
from async_generator import asynccontextmanager
from meltano.core.db import project_engine
from meltano.core.elt_context import ELTContextBuilder
from meltano.core.job import Job, JobFinder
from meltano.core.job.stale_job_failer import StaleJobFailer
from meltano.core.logging import JobLoggingService, OutputLogger
from meltano.core.plugin import PluginRef, PluginType
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.runner import RunnerError
from meltano.core.runner.dbt import DbtRunner
from meltano.core.runner.singer import SingerRunner
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.transform_add_service import TransformAddService
from meltano.core.utils import run_async

from . import cli
from .params import pass_project
from .utils import CliError

DUMPABLES = {
    "catalog": (PluginType.EXTRACTORS, "catalog"),
    "state": (PluginType.EXTRACTORS, "state"),
    "extractor-config": (PluginType.EXTRACTORS, "config"),
    "loader-config": (PluginType.LOADERS, "config"),
}

logger = logging.getLogger(__name__)


def logs(*args, **kwargs):
    logger.info(click.style(*args, **kwargs))


@cli.command()
@click.argument("extractor")
@click.argument("loader")
@click.option("--transform", type=click.Choice(["skip", "only", "run"]), default="skip")
@click.option("--dry", help="Do not actually run.", is_flag=True)
@click.option(
    "--full-refresh",
    help="Perform a full refresh (ignore state left behind by any previous runs)",
    is_flag=True,
)
@click.option(
    "--select",
    "-s",
    help="Select only these specific entities for extraction",
    multiple=True,
    default=[],
)
@click.option(
    "--exclude",
    "-e",
    help="Exclude these specific entities from extraction",
    multiple=True,
    default=[],
)
@click.option("--catalog", help="Extractor catalog file")
@click.option("--state", help="Extractor state file")
@click.option(
    "--dump",
    type=click.Choice(DUMPABLES.keys()),
    help="Dump content of pipeline-specific generated file",
)
@click.option(
    "--job_id", envvar="MELTANO_JOB_ID", help="A custom string to identify the job."
)
@click.option(
    "--force",
    "-f",
    help="Force a new run even when a pipeline with the same Job ID is already running",
    is_flag=True,
)
@pass_project(migrate=True)
def elt(
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
    job_id,
    force,
):
    """
    meltano elt EXTRACTOR_NAME LOADER_NAME

    extractor_name: Which extractor should be used in this extraction
    loader_name: Which loader should be used in this extraction
    """

    select_filter = [*select, *(f"!{entity}" for entity in exclude)]

    job = Job(
        job_id=job_id
        or f'{datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%S")}--{extractor}--{loader}'
    )

    _, Session = project_engine(project)
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
            dump_file(context_builder, dump)
        else:
            run_async(_run_job(project, job, session, context_builder, force=force))
    finally:
        session.close()

    tracker = GoogleAnalyticsTracker(project)
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
    select_filter=[],
    catalog=None,
    state=None,
    plugins_service=None,
):
    transform_name = None
    if transform != "skip":
        transform_name = _find_transform_for_extractor(
            extractor, plugins_service=plugins_service
        )

    return (
        ELTContextBuilder(project, plugins_service=plugins_service)
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


def dump_file(context_builder, dumpable):
    elt_context = context_builder.context()

    try:
        plugin_type, file_id = DUMPABLES[dumpable]
        invoker = elt_context.invoker_for(plugin_type)

        with invoker.prepared(elt_context.session):
            content = invoker.dump(file_id)

        print(content)
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
        with job_logging_service.create_log(job.job_id, job.run_id) as log_file:
            output_logger = OutputLogger(log_file)

            await _run_elt(project, context_builder, output_logger)


@asynccontextmanager
async def _redirect_output(output_logger):
    meltano_stdout = output_logger.out("meltano", stream=sys.stdout, color="blue")
    meltano_stderr = output_logger.out("meltano", color="blue")

    with meltano_stdout.redirect_logging(ignore_errors=(CliError,)):
        async with meltano_stdout.redirect_stdout(), meltano_stderr.redirect_stderr():
            try:
                yield
            except CliError as err:
                err.print()
                raise


async def _run_elt(project, context_builder, output_logger):
    async with _redirect_output(output_logger):
        try:
            elt_context = context_builder.context()

            if not elt_context.only_transform:
                await _run_extract_load(elt_context, output_logger)
            else:
                logs("Extract & load skipped.", fg="yellow")

            if elt_context.transformer:
                await _run_transform(elt_context, output_logger)
            else:
                logs("Transformation skipped.", fg="yellow")
        except RunnerError as err:
            raise CliError(f"ELT could not be completed: {err}") from err


async def _run_extract_load(elt_context, output_logger, **kwargs):  # noqa: WPS231
    extractor = elt_context.extractor.name
    loader = elt_context.loader.name

    extractor_log = output_logger.out(extractor, color="yellow")
    loader_log = output_logger.out(loader, color="green")

    @contextmanager
    def nullcontext():
        yield None

    extractor_out_writer = nullcontext
    loader_out_writer = nullcontext
    if logger.getEffectiveLevel() == logging.DEBUG:
        extractor_out = output_logger.out(f"{extractor} (out)", color="bright_yellow")
        loader_out = output_logger.out(f"{loader} (out)", color="bright_green")

        extractor_out_writer = extractor_out.line_writer
        loader_out_writer = loader_out.line_writer

    logs("Running extract & load...")

    singer_runner = SingerRunner(elt_context)
    try:
        with extractor_log.line_writer() as extractor_log_writer, loader_log.line_writer() as loader_log_writer:
            with extractor_out_writer() as extractor_out_writer, loader_out_writer() as loader_out_writer:
                await singer_runner.run(
                    **kwargs,
                    extractor_log=extractor_log_writer,
                    loader_log=loader_log_writer,
                    extractor_out=extractor_out_writer,
                    loader_out=loader_out_writer,
                )
    except RunnerError as err:
        try:
            code = err.exitcodes[PluginType.EXTRACTORS]
            message = extractor_log.last_line.rstrip() or "(see above)"
            logger.error(
                f"{click.style(f'Extraction failed ({code}):', fg='red')} {message}"
            )
        except KeyError:
            pass

        try:
            code = err.exitcodes[PluginType.LOADERS]
            message = loader_log.last_line.rstrip() or "(see above)"
            logger.error(
                f"{click.style(f'Loading failed ({code}):', fg='red')} {message}"
            )
        except KeyError:
            pass

        raise

    logs("Extract & load complete!", fg="green")


async def _run_transform(elt_context, output_logger, **kwargs):
    transformer_log = output_logger.out(elt_context.transformer.name, color="magenta")

    logs("Running transformation...")

    dbt_runner = DbtRunner(elt_context)
    try:
        with transformer_log.line_writer() as transformer_log_writer:
            await dbt_runner.run(**kwargs, log=transformer_log_writer)
    except RunnerError as err:
        try:
            code = err.exitcodes[PluginType.TRANSFORMERS]
            message = transformer_log.last_line.rstrip() or "(see above)"
            logger.error(
                f"{click.style(f'Transformation failed ({code}):', fg='red')} {message}"
            )
        except KeyError:
            pass

        raise

    logs("Transformation complete!", fg="green")


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
