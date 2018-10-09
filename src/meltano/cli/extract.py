import click
from . import cli
from .params import db_options
from meltano.support.runner.singer import SingerRunner


@cli.command()
@db_options
@click.argument('extractor_name')
@click.option('--loader_name', help="Which loader should be used in this extraction", required=True)
@click.option('--tap-output', help="Output tap stream to this file.")
def extract(job_id, extractor_name, loader_name, tap_output):
    runner = SingerRunner(job_id=job_id,
                          tap_output=tap_output)

    runner.perform(extractor_name, loader_name)
