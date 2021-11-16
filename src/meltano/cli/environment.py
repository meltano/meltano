"""Reusable CLI `--environment` option."""

import click

environment_option = click.option(
    "--environment",
    envvar="MELTANO_ENVIRONMENT",
    help="Meltano environment name",
)
