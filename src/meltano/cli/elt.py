import click
import datetime
import logging
import os
import sys

from . import cli
from .add import add_plugin
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

    _, Session = project_engine(project)
    session = Session()
    job_logging_service = JobLoggingService(project)
    job = Job(
        job_id=job_id or f'job_{datetime.datetime.now().strftime("%Y%m%d-%H:%M:%S.%f")}'
    )

    # fmt: off
    with job.run(session), \
        job_logging_service.create_log(job.job_id, job.run_id) as log_file, \
        OutputLogger(log_file):

        try:
            install_missing_plugins(project, extractor, loader, transform)

            elt_context = (
                ELTContextBuilder(project)
                .with_job(job)
                .with_extractor(extractor)
                .with_loader(loader)
                .context(session)
            )

            if transform != "only":
                run_extract_load(elt_context, session, dry_run=dry)
            else:
                click.secho("Extract & load skipped.", fg="yellow")

            if transform != "skip":
                try:
                    # Use a new session for the Transform Part to address the last
                    # update for Job state not being saved in the DB
                    transform_session = Session()
                    run_transform(elt_context, transform_session, dry_run=dry, models=elt_context.extractor.ref.name)
                finally:
                    transform_session.close()
            else:
                click.secho("Transformation skipped.", fg="yellow")
        except Exception as err:
            logging.error(f"ELT could not complete, an error happened during the process: {err}")
            raise click.Abort()
        finally:
            session.close()
    # fmt: on

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_elt(extractor=extractor, loader=loader, transform=transform)


def run_extract_load(elt_context, session, **kwargs):
    project = elt_context.project
    loader = elt_context.loader.ref
    extractor = elt_context.extractor.ref

    singer_runner = SingerRunner(
        elt_context,
        target_config_dir=project.meltano_dir(loader.type, loader.name),
        tap_config_dir=project.meltano_dir(extractor.type, extractor.name),
    )

    click.echo("Running extract & load...")
    singer_runner.run(session, **kwargs)
    click.secho("Extract & load complete!", fg="green")


def run_transform(elt_context, session, **kwargs):
    dbt_runner = DbtRunner(elt_context)
    click.echo("Running transformation...")
    dbt_runner.run(session, **kwargs)  # TODO: models from elt_context?
    click.secho("Transformation complete!", fg="green")


def install_missing_plugins(
    project: Project, extractor: str, loader: str, transform: str
):
    add_service = ProjectAddService(project)
    config_service = ConfigService(project)

    if transform != "only":
        try:
            config_service.find_plugin(extractor, plugin_type=PluginType.EXTRACTORS)
        except PluginMissingError:
            click.secho(
                f"Extractor '{extractor}' is missing, trying to install it...",
                fg="yellow",
            )
            add_plugin(add_service, project, PluginType.EXTRACTORS, extractor)

        try:
            config_service.find_plugin(loader, plugin_type=PluginType.LOADERS)
        except PluginMissingError:
            click.secho(
                f"Loader '{loader}' is missing, trying to install it...", fg="yellow"
            )
            add_plugin(add_service, project, PluginType.LOADERS, loader)

    if transform != "skip":
        # load the extractor_plugin because we infer the plugin name from it

        try:
            config_service.find_plugin("dbt", plugin_type=PluginType.TRANSFORMERS)
        except PluginMissingError as e:
            click.secho(
                f"Transformer 'dbt' is missing, trying to install it...", fg="yellow"
            )
            add_plugin(add_service, project, PluginType.TRANSFORMERS, "dbt")

        try:
            # the extractor name should match the transform name
            plugin = config_service.find_plugin(
                extractor, plugin_type=PluginType.TRANSFORMS
            )

            # Update dbt_project.yml in case the vars values have changed in meltano.yml
            transform_add_service = TransformAddService(project)
            transform_add_service.update_dbt_project(plugin)
        except PluginMissingError:
            try:
                # Check if there is a default transform for this extractor
                transform_def = PluginDiscoveryService(project).find_plugin(
                    PluginType.TRANSFORMS, extractor
                )

                click.secho(
                    f"Transform '{transform_def.name}' is missing, trying to install it...",
                    fg="yellow",
                )
                add_plugin(
                    add_service, project, PluginType.TRANSFORMS, transform_def.name
                )
            except PluginNotFoundError:
                # There is no default transform for this extractor..
                # Don't panic, everything is cool - just run custom transforms
                pass
