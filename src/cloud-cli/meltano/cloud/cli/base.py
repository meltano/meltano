"""Meltano Cloud CLI base command group."""

from __future__ import annotations

import typing as t
from dataclasses import dataclass
from functools import partial
from pathlib import Path

import click

from meltano.cloud.api.auth import MeltanoCloudAuth
from meltano.cloud.api.config import MeltanoCloudConfig


@dataclass
class MeltanoCloudCLIContext:
    """Meltano Cloud CLI context dataclass.

    Used for storing/passing global objects such as the Cloud CLI config and
    auth, as well as for supporting CLI options that can be set at the group or
    command level.
    """

    config: MeltanoCloudConfig = None  # type: ignore[assignment]
    auth: MeltanoCloudAuth = None  # type: ignore[assignment]

    # Schedule subcommand:
    deployment: str | None = None
    schedule: str | None = None


pass_context = click.make_pass_decorator(MeltanoCloudCLIContext, ensure=True)


def _set_shared_option(ctx: click.Context, opt: click.Option, value: t.Any) -> None:
    if value is not None:
        if getattr(ctx.obj, t.cast(str, opt.name)) is not None:
            raise click.UsageError(
                f"Option '--{opt.name}' must not be specified multiple times."
            )
        setattr(ctx.obj, t.cast(str, opt.name), value)


shared_option = partial(click.option, expose_value=False, callback=_set_shared_option)


@click.group(invoke_without_command=True, no_args_is_help=True)
@click.version_option()
@click.option(
    "--config-path",
    required=False,
    default=None,
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
    help="Path to the Meltano Cloud config file to use.",
)
@pass_context
def cloud(context: MeltanoCloudCLIContext, config_path) -> None:
    """Interface with Meltano Cloud."""
    config = MeltanoCloudConfig.find(config_path=config_path)
    context.config = config
    context.auth = MeltanoCloudAuth(config=config)
