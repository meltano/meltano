import click
import datetime
import logging
import os
import sys

from . import cli
from .utils import add_plugin, install_plugins
from .params import project
from meltano.core.config_service import ConfigService
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
from meltano.core.logging import OutputLogger, JobLoggingService
from meltano.core.elt_context import ELTContextBuilder


@cli.command()
@click.argument("extractor")
@click.argument("loader")
@click.option("--dry", help="Do not actually run.", is_flag=True)
@click.option("--transform", type=click.Choice(["skip", "only", "run"]), default="skip")
@click.option(
    "--job_id", envvar="MELTANO_JOB_ID", help="A custom string to identify the job."
)
@project(migrate=True)
def elt(project, extractor, loader, dry, transform, job_id):
    """
    meltano elt EXTRACTOR_NAME LOADER_NAME

    extractor_name: Which extractor should be used in this extraction
    loader_name: Which loader should be used in this extraction
    """

    job_logging_service = JobLoggingService(project)
    job = Job(
        job_id=job_id or f'job_{datetime.datetime.now().strftime("%Y%m%d-%H:%M:%S.%f")}'
    )

    _, Session = project_engine(project)
    session = Session()
    try:
        with job.run(session), job_logging_service.create_log(
            job.job_id, job.run_id
        ) as log_file, OutputLogger(log_file):
            try:
                success = install_missing_plugins(project, extractor, loader, transform)

                if not success:
                    raise click.Abort()

                elt_context = (
                    ELTContextBuilder(project)
                    .with_job(job)
                    .with_extractor(extractor)
                    .with_loader(loader)
                    .with_transform(transform)
                    .context(session)
                )

                if transform != "only":
                    run_extract_load(elt_context, session, dry_run=dry)
                else:
                    click.secho("Extract & load skipped.", fg="yellow")

                if elt_context.transformer:
                    # Use a new session for the Transform Part to address the last
                    # update for Job state not being saved in the DB
                    transform_session = Session()
                    try:
                        run_transform(elt_context, transform_session, dry_run=dry)
                    finally:
                        transform_session.close()
                else:
                    click.secho("Transformation skipped.", fg="yellow")
            except Exception as err:
                logging.error(
                    f"ELT could not complete, an error happened during the process: {err}"
                )
                raise click.Abort()
    finally:
        session.close()
    # fmt: on

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_elt(extractor=extractor, loader=loader, transform=transform)


def run_extract_load(elt_context, session, **kwargs):
    singer_runner = SingerRunner(elt_context)

    click.echo("Running extract & load...")
    singer_runner.run(session, **kwargs)
    click.secho("Extract & load complete!", fg="green")


def run_transform(elt_context, session, **kwargs):
    dbt_runner = DbtRunner(elt_context)
    click.echo("Running transformation...")
    dbt_runner.run(session, **kwargs)
    click.secho("Transformation complete!", fg="green")


def install_missing_plugins(
    project: Project, extractor: str, loader: str, transform: str
):
    add_service = ProjectAddService(project)
    config_service = ConfigService(project)

    plugins = []
    if transform != "only":
        try:
            config_service.find_plugin(extractor, plugin_type=PluginType.EXTRACTORS)
        except PluginMissingError:
            click.secho(
                f"Extractor '{extractor}' is missing, trying to install it...",
                fg="yellow",
            )
            plugin = add_plugin(
                project, PluginType.EXTRACTORS, extractor, add_service=add_service
            )
            plugins.append(plugin)

        try:
            config_service.find_plugin(loader, plugin_type=PluginType.LOADERS)
        except PluginMissingError:
            click.secho(
                f"Loader '{loader}' is missing, trying to install it...", fg="yellow"
            )
            plugin = add_plugin(
                project, PluginType.LOADERS, loader, add_service=add_service
            )
            plugins.append(plugin)

    if transform != "skip":
        try:
            config_service.find_plugin("dbt", plugin_type=PluginType.TRANSFORMERS)
        except PluginMissingError as e:
            click.secho(
                f"Transformer 'dbt' is missing, trying to install it...", fg="yellow"
            )
            plugin = add_plugin(
                project, PluginType.TRANSFORMERS, "dbt", add_service=add_service
            )
            plugins.append(plugin)

        discovery_service = PluginDiscoveryService(project)
        extractor_plugin_def = discovery_service.find_plugin(
            PluginType.EXTRACTORS, extractor
        )
        try:
            transform_plugin = config_service.find_plugin_by_namespace(
                extractor_plugin_def.namespace, PluginType.TRANSFORMS
            )

            # Update dbt_project.yml in case the vars values have changed in meltano.yml
            transform_add_service = TransformAddService(project)
            transform_add_service.update_dbt_project(transform_plugin)
        except PluginMissingError:
            try:
                # Check if there is a default transform for this extractor
                transform_plugin_def = discovery_service.find_plugin_by_namespace(
                    extractor_plugin_def.namespace, PluginType.TRANSFORMS
                )

                click.secho(
                    f"Transform '{transform_plugin_def.name}' is missing, trying to install it...",
                    fg="yellow",
                )
                add_plugin(
                    project,
                    PluginType.TRANSFORMS,
                    transform_plugin_def.name,
                    add_service=add_service,
                )
                plugins.append(plugin)
            except PluginNotFoundError:
                # There is no default transform for this extractor..
                # Don't panic, everything is cool - just run custom transforms
                pass

    return install_plugins(project, plugins)
