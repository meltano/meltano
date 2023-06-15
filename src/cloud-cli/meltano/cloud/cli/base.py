"""Meltano Cloud CLI base command group."""

from __future__ import annotations

import asyncio
import json
import platform
import typing as t
from dataclasses import dataclass
from functools import partial, wraps
from pathlib import Path

import click
import tabulate

from meltano.cloud import __version__ as version
from meltano.cloud.api.auth import MeltanoCloudAuth
from meltano.cloud.api.config import MeltanoCloudConfig
from meltano.cloud.api.types import CloudDeployment, CloudProject


def run_async(f: t.Callable[..., t.Coroutine[t.Any, t.Any, t.Any]]):
    """Run the given async function using `asyncio.run`.

    Args:
        f: An async function.

    Returns:
        The given function wrapped so as to run within `asyncio.run`.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if platform.system() == "Windows":
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy(),  # type: ignore[attr-defined]
            )
        return asyncio.run(f(*args, **kwargs))

    return wrapper


T = t.TypeVar("T")


class LimitedResult(t.Generic[T]):
    """
    List of items, along with whether or not that list is truncated.

    Used to store lists that are to be printed by `print_formatted_list`.
    """

    def __init__(self, items: t.Union[list[T], None] = None, truncated: bool = False):
        """Initialize items to an empty list and truncated to False."""
        self.items: list[T] = items if items is not None else []
        self.truncated: bool = truncated


def _format_table(
    items: list[T],
    table_format: str,
    format_row: t.Callable[[T], tuple],
    headers: tuple[str, ...],
    colalign: tuple[str, ...],
):
    return tabulate.tabulate(
        [format_row(item) for item in items],
        headers=headers,
        tablefmt=table_format,
        floatfmt=".1f",
        # To avoid a tabulate bug (IndexError), only set colalign if there are items
        colalign=colalign if items else (),
    )


def print_limit_warning():
    """Print a warning that items were truncated due to the --limit option."""
    click.secho(
        "Output truncated due to reaching the item limit. To print more items, "
        "increase the limit using the --limit flag.",
        err=True,
        fg="yellow",
    )


def print_formatted_list(
    results: LimitedResult[T],
    output_format: str,
    format_row: t.Callable[[T], tuple],
    headers: tuple[str, ...],
    colalign: tuple[str, ...],
):
    """
    Format a list of items according to the chosen output format and prints it.

    If the list of items is truncated, also prints a warning telling users to increase
    their item limit.
    """
    if output_format == "terminal":
        output = _format_table(
            results.items,
            "rounded_outline",
            format_row,
            headers,
            colalign,
        )
    elif output_format == "markdown":
        output = _format_table(results.items, "github", format_row, headers, colalign)
    elif output_format == "json":
        output = json.dumps(results.items, indent=2)
    else:
        raise ValueError(f"Unknown format: {output_format}")
    click.echo(output)
    if results.truncated:
        print_limit_warning()


class PaginatedCallable(t.Protocol):
    """Type class defining a paginated function."""

    async def __call__(self, page_size: int, page_token: str | None):
        """Type signature of paginated function."""
        pass


async def get_paginated(
    get_page: PaginatedCallable,
    limit: int,
    max_page_size: int,
) -> LimitedResult:
    """Repeatedly call a paginated function until the item limit is reached."""
    page_token = None
    results: LimitedResult = LimitedResult()
    while True:
        remaining = limit - len(results.items)
        # Make the page size 1 larger than the remaining items required to reach the
        # limit to efficiently detect whether or not there are any truncated items
        page_size = min(remaining + 1, max_page_size)
        response = await get_page(
            page_size=page_size,
            page_token=page_token,
        )

        results.items.extend(response["results"])

        if response["pagination"] and len(results.items) <= limit:
            page_token = response["pagination"]["next_page_token"]
        else:
            results.truncated = len(results.items) > limit
            results.items = results.items[:limit]
            break

    return results


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

    # Project subcommand:
    projects: list[CloudProject] | None = None

    # Deployments subcommand:
    deployments: list[CloudDeployment] | None = None


pass_context = click.make_pass_decorator(MeltanoCloudCLIContext, ensure=True)


def _set_shared_option(ctx: click.Context, opt: click.Option, value: t.Any) -> None:
    if value is not None:
        if getattr(ctx.obj, t.cast(str, opt.name)) is not None:
            raise click.UsageError(
                f"Option '--{opt.name}' must not be specified multiple times.",
            )
        setattr(ctx.obj, t.cast(str, opt.name), value)


shared_option = partial(click.option, expose_value=False, callback=_set_shared_option)


@click.group(invoke_without_command=True, no_args_is_help=True)
@click.version_option(version=version)
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
