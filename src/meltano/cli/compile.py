"""CLI command `meltano compile`."""

from __future__ import annotations

import json
from pathlib import Path

import click

from meltano.cli import cli
from meltano.cli.params import pass_project
from meltano.cli.utils import CliError, InstrumentedCmd
from meltano.core.environment import Environment
from meltano.core.environment_service import EnvironmentService
from meltano.core.manifest import Manifest
from meltano.core.project import Project
from meltano.core.tracking import Tracker
from meltano.core.tracking.contexts import CliEvent


# FIXME: Should this command be named `manifest` instead of `compile`?
@cli.command(cls=InstrumentedCmd, short_help="Compile a Meltano manifest.")
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
@click.pass_context
@pass_project(migrate=True)
def compile(  # noqa: WPS125
    project: Project,
    ctx: click.Context,
    directory: Path,
    indent: int,
):
    """
    Compile a Meltano project into environment-specific manifest files.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#compile
    """
    tracker: Tracker = ctx.obj["tracker"]

    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as ex:
        raise CliError(
            f"Unable to create directory for Meltano manifests {directory}: {ex}"
        ) from ex

    environments = _environments(ctx, project)

    click.echo(
        "Compiling Meltano manifest for environments: "
        + ", ".join("no environment" if x is None else x.name for x in environments)
    )
    for environment in environments:
        path = directory / (
            "meltano-manifest.json"
            if environment is None
            else f"meltano-manifest.{environment.name}.json"
        )
        manifest = Manifest(project=project, environment=environment, path=path)
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
                f"Unable to write Meltano manifest {str(path)!r}: {ex}"
            ) from ex

        click.echo(f"Compiled {path}")
        tracker.track_command_event(CliEvent.inflight)


# FIXME: This command should ignore the default environment and selected
# environment. It should have its own `environment` CLI option(s?), which would
# allow for no-environment to be selected individually (currently you can only
# generate a no-environment manifest by generating them all), and would allow
# for a subset of environments to be selected, rather than one or all.
def _environments(
    ctx: click.Context,
    project: Project,
) -> tuple[Environment | None, ...]:
    if ctx.obj["selected_environment"] and not ctx.obj["is_default_environment"]:
        return [
            Environment.find(
                project.meltano.environments, ctx.obj["selected_environment"]
            )
        ]
    return (None, *EnvironmentService(project).list_environments())
