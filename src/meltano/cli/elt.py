import os
import logging
import click
import datetime

from . import cli
from .add import add_plugin, add_transform
from .params import db_options, project
from meltano.core.config_service import ConfigService
from meltano.core.runner.singer import SingerRunner
from meltano.core.runner.dbt import DbtRunner
from meltano.core.project import Project, ProjectNotFound
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


@cli.command()
@click.argument("extractor")
@click.argument("loader")
@click.option("--dry", help="Do not actually run.", is_flag=True)
@click.option("--transform", type=click.Choice(["skip", "only", "run"]), default="skip")
@click.option(
    "--job_id", envvar="MELTANO_JOB_ID", help="A custom string to identify the job."
)
@db_options
@project
def elt(project, extractor, loader, dry, transform, job_id, engine_uri):
    """
    meltano elt EXTRACTOR_NAME LOADER_NAME

    extractor_name: Which extractor should be used in this extraction
    loader_name: Which loader should be used in this extraction
    """

    # register the project engine
    project_engine(project, engine_uri, default=True)
    install_missing_plugins(project, extractor, loader, transform)

    if job_id is None:
        # Autogenerate a job_id if it is not provided by the user
        job_id = f'job_{datetime.datetime.now().strftime("%Y%m%d-%H:%M:%S.%f")}'

    singer_runner = SingerRunner(
        project,
        job_id=job_id,
        run_dir=os.getenv("SINGER_RUN_DIR", project.meltano_dir("run")),
        target_config_dir=project.meltano_dir(PluginType.LOADERS, loader),
        tap_config_dir=project.meltano_dir(PluginType.EXTRACTORS, extractor),
    )

    dbt_runner = DbtRunner(project)

    try:
        if transform != "only":
            click.echo("Running extract & load...")
            singer_runner.run(extractor, loader, dry_run=dry)
            click.secho("Extract & load complete!", fg="green")
        else:
            click.secho("Extract & load skipped.", fg="yellow")

        if transform != "skip":
            click.echo("Running transformation...")
            dbt_runner.run(dry_run=dry, models=extractor)
            click.secho("Transformation complete!", fg="green")
        else:
            click.secho("Transformation skipped.", fg="yellow")
    except Exception as err:
        click.secho(
            f"ELT could not complete, an error happened during the process.", fg="red"
        )
        click.secho(str(err), err=True)
        raise click.Abort()

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_elt(extractor=extractor, loader=loader, transform=transform)


def install_missing_plugins(
    project: Project, extractor: str, loader: str, transform: str
):
    add_service = ProjectAddService(project)
    config_service = ConfigService(project)

    if transform != "only":
        try:
            config_service.get_plugin(extractor, plugin_type=PluginType.EXTRACTORS)
        except PluginMissingError:
            click.secho(
                f"Extractor '{extractor}' is missing, trying to install it...",
                fg="yellow",
            )
            add_plugin(add_service, project, PluginType.EXTRACTORS, extractor)

        try:
            config_service.get_plugin(loader, plugin_type=PluginType.LOADERS)
        except PluginMissingError:
            click.secho(
                f"Loader '{loader}' is missing, trying to install it...", fg="yellow"
            )
            add_plugin(add_service, project, PluginType.LOADERS, loader)

    if transform != "skip":
        try:
            config_service.get_plugin("dbt", plugin_type=PluginType.TRANSFORMERS)
        except PluginMissingError as e:
            click.secho(
                f"Transformer 'dbt' is missing, trying to install it...", fg="yellow"
            )
            add_plugin(add_service, project, PluginType.TRANSFORMERS, "dbt")

        transform_add_service = TransformAddService(project)
        try:
            # the extractor name should match the transform name
            plugin = config_service.get_plugin(
                extractor, plugin_type=PluginType.TRANSFORMS
            )

            # Update dbt_project.yml in case the vars values have changed in meltano.yml
            transform_add_service.update_dbt_project(plugin)
        except PluginMissingError:
            try:
                # Check if there is a default transform for this extractor
                PluginDiscoveryService(project).find_plugin(
                    PluginType.TRANSFORMS, extractor
                )

                click.secho(
                    f"Transform '{extractor}' is missing, trying to install it...",
                    fg="yellow",
                )
                add_transform(project, extractor)
            except PluginNotFoundError:
                # There is no default transform for this extractor..
                # Don't panic, everything is cool - just run custom transforms
                pass
