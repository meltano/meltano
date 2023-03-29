"""CLI command `meltano compile`."""

from __future__ import annotations

import json
import typing as t
from pathlib import Path

import click

from meltano.cli import cli
from meltano.cli.params import pass_project
from meltano.cli.utils import CliError, InstrumentedCmd
from meltano.core.environment import Environment
from meltano.core.environment_service import EnvironmentService
from meltano.core.manifest import Manifest
from meltano.core.tracking.contexts import CliEvent

if t.TYPE_CHECKING:
    from meltano.core.project import Project
    from meltano.core.tracking import Tracker


@cli.command(cls=InstrumentedCmd, short_help="Compile a Meltano manifest. (beta)")
@click.option(
    "--directory",
    default=".meltano/manifests",
    help="The path of the directory into which the manifest json files will be written",
    type=click.Path(file_okay=False, resolve_path=True, writable=True, path_type=Path),
)
@click.option(
    "--indent",
    default=4,
    help=(
        "The number of spaces to use for indentation in the manifest JSON "
        "files. Set to -1 to remove all non-essential whitespace."
    ),
)
@click.option(
    # Eventually this lint option will just result in calls to the part of
    # `meltano.core` that backs the `meltano lint` command:
    # https://github.com/meltano/meltano/issues/7285
    "--lint/--no-lint",
    default=False,
    help=(
        "Validate the project files and generated manifest files against the "
        "Meltano schema"
    ),
)
@click.pass_context
@pass_project(migrate=True)
def compile(  # noqa: WPS125
    project: Project,
    ctx: click.Context,
    directory: Path,
    lint: bool,
    indent: int,
):
    """
    Compile a Meltano project into environment-specific manifest files.

    This command is in beta, and subject to change without corresponding semantic version updates.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#compile
    """  # noqa: E501
    tracker: Tracker = ctx.obj["tracker"]

    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as ex:
        raise CliError(
            f"Unable to create directory for Meltano manifests {directory}: {ex}",
        ) from ex

    environments = _environments(ctx, project)

    click.echo(
        "Compiling Meltano manifest for environments: "
        + ", ".join("no environment" if x is None else x.name for x in environments),
    )
    for environment in environments:
        path = directory / (
            "meltano-manifest.json"
            if environment is None
            else f"meltano-manifest.{environment.name}.json"
        )
        project.refresh(environment=environment)
        manifest = Manifest(project=project, path=path, check_schema=lint)
        try:
            with open(path, "w") as manifest_file:
                json.dump(
                    manifest.data,
                    manifest_file,
                    indent=indent if indent > 0 else None,
                    sort_keys=True,
                )
        except OSError as ex:
            raise CliError(
                f"Unable to write Meltano manifest {str(path)!r}: {ex}",
            ) from ex

        click.echo(f"Compiled {path}")
        tracker.track_command_event(CliEvent.inflight)


def _environments(
    ctx: click.Context,
    project: Project,
) -> tuple[Environment | None, ...]:
    if ctx.obj["explicit_no_environment"]:
        return (None,)
    if ctx.obj["selected_environment"] and not ctx.obj["is_default_environment"]:
        return (
            Environment.find(
                project.meltano.environments,
                ctx.obj["selected_environment"],
            ),
        )
    return (None, *EnvironmentService(project).list_environments())
