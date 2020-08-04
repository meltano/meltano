import asyncio
import click
import datetime
import logging
import os
import sys
from contextlib import suppress, contextmanager
from async_generator import asynccontextmanager

from . import cli
from .utils import CliError, add_plugin, add_related_plugins, install_plugins
from .params import project
from meltano.core.config_service import ConfigService
from meltano.core.runner import RunnerError
from meltano.core.runner.singer import SingerRunner
from meltano.core.runner.dbt import DbtRunner
from meltano.core.project import Project, ProjectNotFound
from meltano.core.job import Job
from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginMissingError
from meltano.core.project_add_service import ProjectAddService
from meltano.core.transform_add_service import TransformAddService
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.db import project_engine
from meltano.core.plugin_discovery_service import (
    PluginDiscoveryService,
    PluginNotFoundError,
)
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.logging import OutputLogger, JobLoggingService
from meltano.core.elt_context import ELTContextBuilder


logger = logging.getLogger(__name__)


def logs(*args, **kwargs):
    logger.info(click.style(*args, **kwargs))


@cli.command()
@click.argument("extractor")
@click.argument("loader")
@click.option("--dry", help="Do not actually run.", is_flag=True)
@click.option(
    "--full-refresh",
    help="Perform a full refresh (ignore state left behind by any previous runs)",
    is_flag=True,
)
@click.option("--transform", type=click.Choice(["skip", "only", "run"]), default="skip")
@click.option(
    "--job_id", envvar="MELTANO_JOB_ID", help="A custom string to identify the job."
)
@project(migrate=True)
def elt(project, extractor, loader, dry, full_refresh, transform, job_id):
    """
    meltano elt EXTRACTOR_NAME LOADER_NAME

    extractor_name: Which extractor should be used in this extraction
    loader_name: Which loader should be used in this extraction
    """

    job = Job(
        job_id=job_id or f'job_{datetime.datetime.now().strftime("%Y%m%d-%H:%M:%S.%f")}'
    )

    _, Session = project_engine(project)
    session = Session()

    try:
        job_logging_service = JobLoggingService(project)

        with job.run(session), job_logging_service.create_log(
            job.job_id, job.run_id
        ) as log_file:
            output_logger = OutputLogger(log_file)

            run_async(
                run_elt(
                    project,
                    job,
                    extractor,
                    loader,
                    transform,
                    output_logger=output_logger,
                    session=session,
                    dry_run=dry,
                    full_refresh=full_refresh,
                )
            )
    finally:
        session.close()

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_elt(extractor=extractor, loader=loader, transform=transform)


def run_async(coro):
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(coro)
    except asyncio.CancelledError:
        pass
    finally:
        # The below is taken from https://stackoverflow.com/a/58532304
        # and inspired by to Python 3.7's `asyncio.run`
        all_tasks = asyncio.gather(
            *asyncio.Task.all_tasks(loop), return_exceptions=True
        )
        all_tasks.cancel()
        with suppress(asyncio.CancelledError):
            loop.run_until_complete(all_tasks)
        loop.run_until_complete(loop.shutdown_asyncgens())


@asynccontextmanager
async def redirect_output(output_logger):
    meltano_stdout = output_logger.out("meltano", stream=sys.stdout, color="blue")
    meltano_stderr = output_logger.out("meltano", color="blue")

    with meltano_stdout.redirect_logging(ignore_errors=(CliError,)):
        async with meltano_stdout.redirect_stdout(), meltano_stderr.redirect_stderr():
            yield


async def run_elt(
    project,
    job,
    extractor,
    loader,
    transform,
    output_logger,
    session,
    dry_run=False,
    full_refresh=False,
):
    async with redirect_output(output_logger):
        try:
            success = install_missing_plugins(project, extractor, loader, transform)

            if not success:
                raise CliError("Failed to install missing plugins")

            elt_context = (
                ELTContextBuilder(project)
                .with_job(job)
                .with_extractor(extractor)
                .with_loader(loader)
                .with_transform(transform)
                .context(session)
            )

            if transform != "only":
                await run_extract_load(
                    elt_context,
                    output_logger,
                    session,
                    dry_run=dry_run,
                    full_refresh=full_refresh,
                )
            else:
                logs("Extract & load skipped.", fg="yellow")

            if elt_context.transformer:
                await run_transform(
                    elt_context, output_logger, session, dry_run=dry_run
                )
            else:
                logs("Transformation skipped.", fg="yellow")
        except RunnerError as err:
            raise CliError(f"ELT could not be completed: {err}") from err


async def run_extract_load(elt_context, output_logger, session, **kwargs):
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
                    session,
                    **kwargs,
                    extractor_log=extractor_log_writer,
                    loader_log=loader_log_writer,
                    extractor_out=extractor_out_writer,
                    loader_out=loader_out_writer,
                )
    except RunnerError as err:
        try:
            code = err.exitcodes["extractor"]
            message = extractor_log.last_line.rstrip() or "(see above)"
            logger.error(
                f"{click.style(f'Extraction failed ({code}):', fg='red')} {message}"
            )
        except KeyError:
            pass

        try:
            code = err.exitcodes["loader"]
            message = loader_log.last_line.rstrip() or "(see above)"
            logger.error(
                f"{click.style(f'Loading failed ({code}):', fg='red')} {message}"
            )
        except KeyError:
            pass

        raise

    logs("Extract & load complete!", fg="green")


async def run_transform(elt_context, output_logger, session, **kwargs):
    transformer_log = output_logger.out(elt_context.transformer.name, color="magenta")

    logs("Running transformation...")

    dbt_runner = DbtRunner(elt_context)
    try:
        with transformer_log.line_writer() as transformer_log_writer:
            await dbt_runner.run(session, **kwargs, log=transformer_log_writer)
    except RunnerError as err:
        try:
            code = err.exitcodes["transformer"]
            message = transformer_log.last_line.rstrip() or "(see above)"
            logger.error(
                f"{click.style(f'Transformation failed ({code}):', fg='red')} {message}"
            )
        except KeyError:
            pass

        raise

    logs("Transformation complete!", fg="green")


def install_missing_plugins(
    project: Project, extractor: str, loader: str, transform: str
):
    config_service = ConfigService(project)
    discovery_service = PluginDiscoveryService(project, config_service=config_service)
    add_service = ProjectAddService(
        project,
        plugin_discovery_service=discovery_service,
        config_service=config_service,
    )

    plugins = []
    if transform != "only":
        try:
            config_service.find_plugin(extractor, plugin_type=PluginType.EXTRACTORS)
        except PluginMissingError:
            logs(
                f"Extractor '{extractor}' is missing, adding it to your project...",
                fg="yellow",
            )
            plugin = add_plugin(
                project, PluginType.EXTRACTORS, extractor, add_service=add_service
            )
            plugins.append(plugin)

        try:
            config_service.find_plugin(loader, plugin_type=PluginType.LOADERS)
        except PluginMissingError:
            logs(
                f"Loader '{loader}' is missing, adding it to your project...",
                fg="yellow",
            )
            plugin = add_plugin(
                project, PluginType.LOADERS, loader, add_service=add_service
            )
            plugins.append(plugin)

    if transform != "skip":
        try:
            extractor_plugin_def = discovery_service.find_plugin(
                PluginType.EXTRACTORS, extractor
            )
            # Check if there is a default transform for this extractor
            transform_plugin_def = discovery_service.find_plugin_by_namespace(
                PluginType.TRANSFORMS, extractor_plugin_def.namespace
            )

            try:
                config_service.find_plugin(
                    transform_plugin_def.name, plugin_type=PluginType.TRANSFORMS
                )
            except PluginMissingError:
                logs(
                    f"Transform '{transform_plugin_def.name}' is missing, adding it to your project...",
                    fg="yellow",
                )
                plugin = add_plugin(
                    project,
                    PluginType.TRANSFORMS,
                    transform_plugin_def.name,
                    add_service=add_service,
                )
                plugins.append(plugin)
        except PluginNotFoundError:
            # There is no default transform for this extractor..
            # Don't panic, everything is cool - just run custom transforms
            try:
                config_service.find_plugin("dbt", plugin_type=PluginType.TRANSFORMERS)
            except PluginMissingError:
                logs(
                    f"Transformer 'dbt' is missing, adding it to your project...",
                    fg="yellow",
                )
                plugin = add_plugin(
                    project, PluginType.TRANSFORMERS, "dbt", add_service=add_service
                )
                plugins.append(plugin)

    if not plugins:
        return True

    related_plugins = add_related_plugins(
        project, plugins, add_service=add_service, plugin_types=[PluginType.FILES]
    )
    plugins.extend(related_plugins)

    # We will install the plugins in reverse order, since dependencies
    # are listed after their dependents in `related_plugins`, but should
    # be installed first.
    plugins.reverse()

    return install_plugins(project, plugins, reason=PluginInstallReason.ADD)
