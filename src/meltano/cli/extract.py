import click
import logging

from . import cli
from .params import db_options
from meltano.core.runner.singer import SingerRunner
from meltano.core.runner.dbt import DbtRunner
from meltano.core.project import Project


@cli.command()
@db_options
@click.argument("job_id", envvar="MELTANO_JOB_ID")
@click.argument("extractor_name")
@click.option(
    "--loader_name",
    help="Which loader should be used in this extraction",
    required=True,
)
@click.option("--tap-output", help="Output tap stream to this file.")
def extract(job_id, extractor_name, loader_name, tap_output):
    try:
        project = Project.find()
        runner = SingerRunner(project, job_id=job_id, tap_output=tap_output)

        runner.perform(extractor_name, loader_name)
    except Exception as err:
        click.secho(f"Extraction failed: {err}.", fg="red")
        raise click.Abort()


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
@click.option("--tap-output", help="Output tap stream to this file.")
@click.option("--dry", help="Do not actually run.", is_flag=True)
def elt(job_id, extractor, loader, tap_output, dry):
    try:
        project = Project.find()
        click.echo("Running extract & load...")
        runner = SingerRunner(project, job_id=job_id, tap_output=tap_output)

        runner.perform(extractor, loader, dry_run=dry)
        click.secho("Extract & load complete!", fg="green")

        click.echo("Running tranformations...")
        dbt_runner = DbtRunner(project)
        dbt_runner.perform(dry_run=dry)
        click.secho("Transform complete!", fg="green")
    except Exception as err:
        logging.exception(err)
        click.secho(f"Extraction failed: {err}.", fg="red")
        raise click.Abort()
