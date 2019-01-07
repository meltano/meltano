import os
import logging
import click
import datetime

from . import cli
from .params import db_options
from meltano.core.runner.singer import SingerRunner
from meltano.core.runner.dbt import DbtRunner
from meltano.core.project import Project, ProjectNotFound
from meltano.core.plugin import PluginType


@cli.command()
@db_options
@click.argument("extractor")
@click.argument("loader")
@click.option("--dry", help="Do not actually run.", is_flag=True)
@click.option("--transform", type=click.Choice(["skip", "only", "run"]), default="skip")
@click.option("--job_id", envvar="MELTANO_JOB_ID", help="A custom string to identify the job.")
def elt(extractor, loader, dry, transform, job_id):
    """
    meltano elt ${extractor_name} ${loader_name}

    extractor_name: Which extractor should be used in this extraction
    loader_name: Which loader should be used in this extraction
    """
    try:
        project = Project.find()
    except ProjectNotFound as e:
        raise click.ClickException(e)

    if job_id is None:
        # Autogenerate a job_id if it is not provided by the user
        job_id = f'job{datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")}'

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
            singer_runner.perform(extractor, loader, dry_run=dry)
            click.secho("Extract & load complete!", fg="green")
        else:
            click.secho("Extract & load skipped.", fg="yellow")

        if transform != "skip":
            click.echo("Running transformation...")
            dbt_runner.perform(dry_run=dry, models=extractor)
            click.secho("Transformation complete!", fg="green")
        else:
            click.secho("Transformation skipped.", fg="yellow")
    except Exception as err:
        raise click.ClickException(
            f"ELT could not complete, an error happened during the process: {err}."
        )
