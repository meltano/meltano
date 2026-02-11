"""Defines `meltano elt` command."""

from __future__ import annotations

import logging
import platform
import typing as t
from contextlib import asynccontextmanager, nullcontext, suppress
from datetime import datetime, timezone

import click
import structlog

from meltano.cli.params import (
    UUIDParamType,
    get_install_options,
    pass_project,
)
from meltano.cli.utils import CliEnvironmentBehavior, CliError, PartialInstrumentedCmd
from meltano.core._state import StateStrategy
from meltano.core.db import project_engine
from meltano.core.elt_context import ELTContextBuilder
from meltano.core.job import Job, JobFinder
from meltano.core.job.stale_job_failer import fail_stale_jobs
from meltano.core.logging import JobLoggingService, OutputLogger
from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.runner import RunnerError
from meltano.core.runner.dbt import DbtRunner
from meltano.core.runner.singer import SingerRunner
from meltano.core.tracking.contexts import CliEvent, PluginsTrackingContext
from meltano.core.utils import new_run_id, run_async

if t.TYPE_CHECKING:
    import uuid

    from sqlalchemy.orm import Session

    from meltano.cli.params import InstallPlugins
    from meltano.core.elt_context import ELTContext
    from meltano.core.plugin.base import PluginDefinition
    from meltano.core.project import Project
    from meltano.core.tracking import Tracker

DUMPABLES = {
    "catalog": (PluginType.EXTRACTORS, "catalog"),
    "state": (PluginType.EXTRACTORS, "state"),
    "extractor-config": (PluginType.EXTRACTORS, "config"),
    "loader-config": (PluginType.LOADERS, "config"),
}

logger = structlog.stdlib.get_logger(__name__)

install, no_install, only_install = get_install_options(include_only_install=True)


class ELOptions:
    """Namespace for all options shared by the `el` and `elt` commands."""

    extractor = click.argument("extractor")
    loader = click.argument("loader")
    transform = click.option(
        "--transform",
        type=click.Choice(["skip", "only", "run"]),
    )
    dry = click.option("--dry", help="Do not actually run.", is_flag=True)
    full_refresh = click.option(
        "--full-refresh",
        help="Perform a full refresh (ignore state left behind by any previous runs).",
        envvar="MELTANO_RUN_FULL_REFRESH",
        is_flag=True,
    )
    refresh_catalog = click.option(
        "--refresh-catalog",
        help="Invalidates catalog cache and forces running discovery before this run.",
        is_flag=True,
    )
    select = click.option(
        "--select",
        "-s",
        help="Select only these specific entities for extraction.",
        multiple=True,
        default=[],
    )
    exclude = click.option(
        "--exclude",
        "-e",
        help="Exclude these specific entities from extraction.",
        multiple=True,
        default=[],
    )
    catalog = click.option("--catalog", help="Extractor catalog file.")
    state = click.option("--state", help="Extractor state file.")
    dump = click.option(
        "--dump",
        type=click.Choice(tuple(DUMPABLES)),
        help="Dump content of pipeline-specific generated file.",
    )
    state_id = click.option(
        "--state-id",
        envvar="MELTANO_STATE_ID",
        help="A custom string to identify the job.",
    )
    force = click.option(
        "--force",
        "-f",
        help=(
            "Force a new run even when a pipeline with the same state ID is "
            "already running."
        ),
        is_flag=True,
    )
    merge_state = click.option(
        "--merge-state",
        is_flag=True,
        help="Merges state with that of previous runs.",
        hidden=True,
    )
    state_strategy = click.option(
        "--state-strategy",
        type=click.Choice(StateStrategy),
        help="Strategy to use for state updates.",
        default=StateStrategy.auto.value,
    )
    run_id = click.option(
        "--run-id",
        type=UUIDParamType(),
        help="Provide a UUID to use as the run ID.",
    )


@click.command(
    cls=PartialInstrumentedCmd,
    short_help="Run an EL pipeline to Extract and Load data.",
    environment_behavior=CliEnvironmentBehavior.environment_optional_use_default,
)
@ELOptions.extractor
@ELOptions.loader
@ELOptions.dry
@ELOptions.full_refresh
@ELOptions.refresh_catalog
@ELOptions.select
@ELOptions.exclude
@ELOptions.catalog
@ELOptions.state
@ELOptions.dump
@ELOptions.state_id
@ELOptions.force
@ELOptions.merge_state
@ELOptions.state_strategy
@install
@no_install
@only_install
@ELOptions.run_id
@click.pass_context
@pass_project(migrate=True)
@run_async
async def el(  # WPS408
    project: Project,
    ctx: click.Context,
    *,
    extractor: str,
    loader: str,
    dry: bool,
    full_refresh: bool,
    refresh_catalog: bool,
    select: list[str],
    exclude: list[str],
    catalog: str | None,
    state: str | None,
    dump: str | None,
    state_id: str | None,
    force: bool,
    merge_state: bool,
    state_strategy: str,
    run_id: uuid.UUID | None,
    install_plugins: InstallPlugins,
) -> None:
    """Run an EL pipeline to Extract and Load data.

    meltano el '<extractor_name>' '<loader_name>'

    extractor_name: extractor to be used in this pipeline.
    loader_name: loader to be used in this pipeline.

    \b
    Read more at https://docs.meltano.com/reference/command-line-interface#el
    """  # noqa: D301
    await _run_el_command(
        project=project,
        ctx=ctx,
        extractor=extractor,
        loader=loader,
        transform=None,
        dry=dry,
        full_refresh=full_refresh,
        refresh_catalog=refresh_catalog,
        select=select,
        exclude=exclude,
        catalog=catalog,
        state=state,
        dump=dump,
        state_id=state_id,
        force=force,
        merge_state=merge_state,
        state_strategy=state_strategy,
        install_plugins=install_plugins,
        run_id=run_id,
    )


@click.command(
    cls=PartialInstrumentedCmd,
    short_help="Run an ELT pipeline to Extract, Load, and Transform data.",
    environment_behavior=CliEnvironmentBehavior.environment_optional_use_default,
)
@ELOptions.extractor
@ELOptions.loader
@ELOptions.transform
@ELOptions.dry
@ELOptions.full_refresh
@ELOptions.refresh_catalog
@ELOptions.select
@ELOptions.exclude
@ELOptions.catalog
@ELOptions.state
@ELOptions.dump
@ELOptions.state_id
@ELOptions.force
@ELOptions.merge_state
@ELOptions.state_strategy
@install
@no_install
@only_install
@ELOptions.run_id
@click.pass_context
@pass_project(migrate=True)
@run_async
async def elt(  # WPS408
    project: Project,
    ctx: click.Context,
    *,
    extractor: str,
    loader: str,
    transform: str,
    dry: bool,
    full_refresh: bool,
    refresh_catalog: bool,
    select: list[str],
    exclude: list[str],
    catalog: str | None,
    state: str | None,
    dump: str | None,
    state_id: str | None,
    force: bool,
    merge_state: bool,
    state_strategy: str,
    install_plugins: InstallPlugins,
    run_id: uuid.UUID | None,
) -> None:
    """Run an ELT pipeline to Extract, Load, and Transform data.

    meltano elt '<extractor_name>' '<loader_name>'

    extractor_name: extractor to be used in this pipeline.
    loader_name: loader to be used in this pipeline.

    \b
    Read more at https://docs.meltano.com/reference/command-line-interface#elt
    """  # noqa: D301
    logger.warning("The `elt` command is deprecated in favor of `el`")
    await _run_el_command(
        project=project,
        ctx=ctx,
        extractor=extractor,
        loader=loader,
        transform=transform,
        dry=dry,
        full_refresh=full_refresh,
        refresh_catalog=refresh_catalog,
        select=select,
        exclude=exclude,
        catalog=catalog,
        state=state,
        dump=dump,
        state_id=state_id,
        force=force,
        merge_state=merge_state,
        state_strategy=state_strategy,
        install_plugins=install_plugins,
        run_id=run_id,
    )


async def _run_el_command(
    project: Project,
    ctx: click.Context,
    *,
    extractor: str,
    loader: str,
    transform: str | None,
    dry: bool,
    full_refresh: bool,
    refresh_catalog: bool,
    select: list[str],
    exclude: list[str],
    catalog: str | None,
    state: str | None,
    dump: str | None,
    state_id: str | None,
    force: bool,
    merge_state: bool,
    state_strategy: str,
    install_plugins: InstallPlugins,
    run_id: uuid.UUID | None,
) -> None:
    if platform.system() == "Windows":
        raise CliError(  # noqa: TRY003
            "ELT command not supported on Windows. Please use the run command "  # noqa: EM101
            "as documented here: "
            "https://docs.meltano.com/reference/command-line-interface#run",
        )

    tracker: Tracker = ctx.obj["tracker"]

    # We no longer set a default choice for transform, so that we can detect
    # explicit usages of the `--transform` option if transform is `None` we
    # still need manually default to skip after firing the tracking event above
    # TODO: Remove the transform option entirely in a future release
    transform = transform or "skip"

    select_filter = [*select, *(f"!{entity}" for entity in exclude)]

    # Bind run_id at the start of the CLI entrypoint
    run_id = run_id or new_run_id()
    structlog.contextvars.bind_contextvars(run_id=str(run_id))

    _state_strategy = StateStrategy.from_cli_args(
        merge_state=merge_state,
        state_strategy=state_strategy,
    )

    job = Job(
        job_name=state_id
        or (
            f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H%M%S')}"
            f"--{extractor}--{loader}"
        ),
        run_id=run_id,
    )
    _, Session = project_engine(project)  # noqa: N806
    session = Session()
    try:
        context_builder = _elt_context_builder(
            project,
            job,
            session,
            extractor,
            loader,
            transform,
            dry_run=dry,
            full_refresh=full_refresh,
            refresh_catalog=refresh_catalog,
            select_filter=select_filter,
            catalog=catalog,
            state=state,
            state_strategy=_state_strategy,
            run_id=run_id,
        )

        if dump:
            await dump_file(context_builder, dump)
        else:
            await _run_job(
                tracker,
                project,
                job,
                session,
                context_builder,
                install_plugins,
                force=force,
            )
    except Exception as err:
        tracker.track_command_event(CliEvent.failed)
        raise err  # noqa: TRY201
    finally:
        session.close()

    tracker.track_command_event(CliEvent.completed)


def _elt_context_builder(
    project: Project,
    job: Job,
    session: Session,
    extractor: str,
    loader: str,
    transform: str,
    *,
    dry_run: bool = False,
    full_refresh: bool = False,
    refresh_catalog: bool = False,
    select_filter: list[str],
    catalog: str | None = None,
    state: str | None = None,
    state_strategy: StateStrategy,
    run_id: uuid.UUID | None = None,
) -> ELTContextBuilder:
    transform_name = None
    if transform != "skip":
        transform_name = _find_transform_for_extractor(project, extractor)

    return (
        ELTContextBuilder(project)
        .with_session(session)
        .with_job(job)
        .with_extractor(extractor)
        .with_loader(loader)
        .with_transform(transform_name or transform)
        .with_dry_run(dry_run=dry_run)
        .with_only_transform(only_transform=(transform == "only"))
        .with_full_refresh(full_refresh=full_refresh)
        .with_refresh_catalog(refresh_catalog=refresh_catalog)
        .with_select_filter(select_filter)
        .with_catalog(catalog)
        .with_state(state)
        .with_state_strategy(state_strategy=state_strategy)
        .with_run_id(run_id)
    )


async def dump_file(context_builder: ELTContextBuilder, dumpable: str) -> None:
    """Dump the given dumpable for this pipeline."""
    elt_context = context_builder.context()

    try:
        plugin_type, file_id = DUMPABLES[dumpable]
        invoker = elt_context.invoker_for(plugin_type)

        async with invoker.prepared(elt_context.session):
            content = await invoker.dump(file_id)

        click.echo(content)
    except FileNotFoundError as err:
        raise CliError(f"Could not find {dumpable} file for this pipeline") from err  # noqa: EM102, TRY003
    except Exception as err:
        raise CliError(f"Could not dump {dumpable}: {err}") from err  # noqa: EM102, TRY003


async def _run_job(
    tracker: Tracker,
    project: Project,
    job: Job,
    session: Session,
    context_builder: ELTContextBuilder,
    install_plugins: InstallPlugins,
    *,
    force: bool = False,
) -> None:
    fail_stale_jobs(session, job.job_name)

    if not force and (existing := JobFinder(job.job_name).latest_running(session)):
        raise CliError(  # noqa: TRY003
            f"Another '{job.job_name}' pipeline is already running which "  # noqa: EM102
            f"started at {existing.started_at}. To ignore this check use "
            "the '--force' option.",
        )

    async with job.run(session):
        job_logging_service = JobLoggingService(project)
        log_file = job_logging_service.generate_log_name(job.job_name, job.run_id)

        output_logger = OutputLogger(log_file)
        context_builder.set_base_output_logger(output_logger)

        log = logger.bind(name="meltano", run_id=str(job.run_id), state_id=job.job_name)

        await _run_elt(tracker, log, context_builder, output_logger, install_plugins)


@asynccontextmanager
async def _redirect_output(
    log: structlog.stdlib.BoundLogger,
    output_logger: OutputLogger,
) -> t.AsyncGenerator[None, None]:
    meltano_stdout = output_logger.out(
        "meltano",
        log.bind(stdio="stdout", cmd_type="elt"),
    )
    meltano_stderr = output_logger.out(
        "meltano",
        log.bind(stdio="stderr", cmd_type="elt"),
    )

    with meltano_stdout.redirect_logging(ignore_errors=(CliError,)):
        async with meltano_stdout.redirect_stdout(), meltano_stderr.redirect_stderr():
            try:
                yield
            except CliError as err:
                err.print()
                raise


async def _run_elt(
    tracker: Tracker,
    log: structlog.stdlib.BoundLogger,
    context_builder: ELTContextBuilder,
    output_logger: OutputLogger,
    install_plugins: InstallPlugins,
) -> None:
    elt_context = context_builder.context()
    plugins = [elt_context.extractor, elt_context.loader]

    if elt_context.only_transform:
        plugins.append(elt_context.transformer)

    await install_plugins(
        elt_context.project,
        plugins,
        reason=PluginInstallReason.AUTO,
    )

    async with _redirect_output(log, output_logger):
        try:
            tracker.add_contexts(PluginsTrackingContext.from_elt_context(elt_context))
            tracker.track_command_event(CliEvent.inflight)

            if elt_context.only_transform:
                log.info("Extract & load skipped.")
            else:
                await _run_extract_load(log, elt_context, output_logger)

            if elt_context.transformer:
                log.warning(
                    "The option to run a transformation is deprecated and will be "
                    "removed in a future version.",
                )
                await _run_transform(log, elt_context, output_logger)
            else:
                log.info("Transformation skipped.")
        except RunnerError as err:
            raise CliError(  # noqa: TRY003
                f"ELT could not be completed: {err}.\nFor more detailed log "  # noqa: EM102
                "messages re-run the command using 'meltano "
                "--log-level=debug ...' CLI flag.\nNote that you can also "
                f"check the generated log file at '{output_logger.file}'.\n"
                "For more information on debugging and logging: "
                "https://docs.meltano.com/reference/command-line-interface#debugging",
            ) from err


async def _run_extract_load(
    log: structlog.stdlib.BoundLogger,
    elt_context: ELTContext,
    output_logger: OutputLogger,
    **kwargs: t.Any,
) -> None:
    extractor = elt_context.extractor.name  # type: ignore[union-attr]
    loader = elt_context.loader.name  # type: ignore[union-attr]

    stderr_log = logger.bind(
        run_id=str(elt_context.job.run_id),  # type: ignore[union-attr]
        state_id=elt_context.job.job_name,  # type: ignore[union-attr]
        stdio="stderr",
    )

    extractor_log = output_logger.out(extractor, stderr_log.bind(cmd_type="extractor"))
    loader_log = output_logger.out(loader, stderr_log.bind(cmd_type="loader"))

    extractor_out_writer_ctxmgr = nullcontext
    loader_out_writer_ctxmgr = nullcontext
    if logger.getEffectiveLevel() == logging.DEBUG:
        stdout_log = logger.bind(
            run_id=str(elt_context.job.run_id),  # type: ignore[union-attr]
            state_id=elt_context.job.job_name,  # type: ignore[union-attr]
            stdio="stdout",
        )
        extractor_out = output_logger.out(
            f"{extractor} (out)",
            stdout_log.bind(cmd_type="extractor"),
            logging.DEBUG,
        )
        loader_out = output_logger.out(
            f"{loader} (out)",
            stdout_log.bind(cmd_type="loader"),
            logging.DEBUG,
        )

        extractor_out_writer_ctxmgr = extractor_out.line_writer  # type: ignore[assignment]
        loader_out_writer_ctxmgr = loader_out.line_writer  # type: ignore[assignment]

    log.info(
        "Running extract & load...",
    )

    singer_runner = SingerRunner(elt_context)
    try:
        # Once Python 3.9 support has been dropped, consolidate these
        # with-statements by using parentheses.
        with extractor_log.line_writer() as extractor_log_writer:  # noqa: SIM117
            with loader_log.line_writer() as loader_log_writer:
                with extractor_out_writer_ctxmgr() as extractor_out_writer:
                    with loader_out_writer_ctxmgr() as loader_out_writer:
                        await singer_runner.run(
                            **kwargs,
                            extractor_log=extractor_log_writer,
                            loader_log=loader_log_writer,
                            extractor_out=extractor_out_writer,
                            loader_out=loader_out_writer,
                        )
    except RunnerError as err:
        with suppress(KeyError):
            code = err.exitcodes[PluginType.EXTRACTORS]
            message = extractor_log.last_line.rstrip() or "(see above)"
            log.error("Extraction failed", code=code, message=message)  # noqa: TRY400
        with suppress(KeyError):
            code = err.exitcodes[PluginType.LOADERS]
            message = loader_log.last_line.rstrip() or "(see above)"
            log.error("Loading failed", code=code, message=message)  # noqa: TRY400
        raise

    log.info("Extract & load complete!")


async def _run_transform(
    log: structlog.stdlib.BoundLogger,
    elt_context: ELTContext,
    output_logger: OutputLogger,
    **kwargs: t.Any,
) -> None:
    stderr_log = logger.bind(
        run_id=str(elt_context.job.run_id),  # type: ignore[union-attr]
        state_id=elt_context.job.job_name,  # type: ignore[union-attr]
        stdio="stderr",
        cmd_type="transformer",
    )

    transformer_log = output_logger.out(
        elt_context.transformer.name,  # type: ignore[union-attr]
        stderr_log,
    )

    log.info("Running transformation...")

    dbt_runner = DbtRunner(elt_context)
    try:
        with transformer_log.line_writer() as transformer_log_writer:
            await dbt_runner.run(**kwargs, log=transformer_log_writer)
    except RunnerError as err:
        with suppress(KeyError):
            code = err.exitcodes[PluginType.TRANSFORMERS]
            message = transformer_log.last_line.rstrip() or "(see above)"
            log.error("Transformation failed", code=code, message=message)  # noqa: TRY400
        raise

    log.info("Transformation complete!")


def _find_extractor(project: Project, extractor_name: str) -> PluginDefinition:
    return project.plugins.locked_definition_service.find_definition(
        PluginType.EXTRACTORS,
        extractor_name,
    )


def _find_transform_for_extractor(
    project: Project,
    extractor_name: str,
) -> str | None:
    try:
        # Check if there is a default transform for this extractor
        transform_plugin_def = project.plugins.find_plugin_by_namespace(
            PluginType.TRANSFORMS,
            _find_extractor(project, extractor_name).namespace,
        )

        # Check if the transform has been added to the project
        transform_plugin = project.plugins.get_plugin(transform_plugin_def)

        return transform_plugin.name  # noqa: TRY300
    except PluginNotFoundError:
        return None
