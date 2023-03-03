"""Meltano Cloud CLI base command group."""

from __future__ import annotations

import click

from meltano.cloud.api.auth import MeltanoCloudAuth
from meltano.cloud.api.config import MeltanoCloudConfig


@click.group(invoke_without_command=True, no_args_is_help=True)
@click.version_option()
@click.option(
    "--config-path",
    required=False,
    default=None,
    type=click.Path(),
    help="Path to the meltano cloud config file to use.",
)
@click.pass_context
def cloud(ctx: click.Context, config_path) -> None:
    """Interface with Meltano Cloud.

    Args:
        ctx: the click context
        config_path: path to config to use
    """
    ctx.ensure_object(dict)
    ctx.obj["config"] = MeltanoCloudConfig.find(config_path=config_path)
    ctx.obj["auth"] = MeltanoCloudAuth()
