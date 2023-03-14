"""Meltano Cloud CLI base command group."""

from __future__ import annotations

from pathlib import Path

import click

from meltano.cloud.api.auth import MeltanoCloudAuth
from meltano.cloud.api.config import MeltanoCloudConfig


@click.group(invoke_without_command=True, no_args_is_help=True)
@click.version_option()
@click.option(
    "--config-path",
    required=False,
    default=None,
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
    help="Path to the Meltano Cloud config file to use.",
)
@click.pass_context
def cloud(ctx: click.Context, config_path) -> None:
    """Interface with Meltano Cloud."""
    ctx.ensure_object(dict)
    config = MeltanoCloudConfig.find(config_path=config_path)
    ctx.obj["config"] = config
    ctx.obj["auth"] = MeltanoCloudAuth(config=config)
