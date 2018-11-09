import os
import logging
import click

from . import cli
from .params import db_options
from meltano.core.runner.singer import SingerRunner
from meltano.core.runner.dbt import DbtRunner
from meltano.core.dbt_service import DbtService
from meltano.core.project import Project
from meltano.core.plugin import PluginType


@cli.command()
@db_options
@click.argument("job_id", envvar="MELTANO_JOB_ID")
@click.option(
    "--extractor",
    help="Which extractor should be used in this extraction",
    required=True,
)
@click.option(
    "--loader", help="Which loader should be used in this extraction", required=True
)
@click.option("--dry", help="Do not actually run.", is_flag=True)
@click.option(
    "--transform", type=click.Choice(["skip", "only", "auto"]), default="auto"
)
def elt(job_id, extractor, loader, dry, transform):
    project = Project.find()

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
            dbt_runner.perform(dry_run=dry)
            click.secho("Transformation complete!", fg="green")
        else:
            click.secho("Transformation skipped.", fg="yellow")
    except Exception as err:
        logging.exception(err)
        click.secho(f"Extraction failed: {err}.", fg="red")
        raise click.Abort()
