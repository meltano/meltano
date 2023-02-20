"""Meltano Cloud CLI."""

from __future__ import annotations

import click

from meltano.cloud.api.auth import MeltanoCloudAuth
from meltano.cloud.api.config import MeltanoCloudConfig


@click.group(invoke_without_command=True, no_args_is_help=True)
@click.version_option()
@click.pass_context
def cloud(ctx: click.Context) -> None:
    """Interface with Meltano Cloud.

    Args:
        ctx: the click context
    """
    ctx.ensure_object(dict)
    ctx.obj["config"] = MeltanoCloudConfig.find()
    ctx.obj["auth"] = MeltanoCloudAuth()


def main() -> int:
    """Run the Meltano Cloud CLI.

    Returns:
        The CLI exit code.
    """
    try:
        cloud()
    except Exception:
        return 1
    return 0
