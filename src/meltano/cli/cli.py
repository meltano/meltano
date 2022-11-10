"""Definition of the top-level Click group for the Meltano CLI."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import NoReturn

import click

import meltano
from meltano.cli.utils import InstrumentedGroup
from meltano.core.behavior.versioned import IncompatibleVersionError
from meltano.core.error import MeltanoConfigurationError
from meltano.core.logging import LEVELS, setup_logging
from meltano.core.project import Project, ProjectNotFound
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.tracking import CliContext, Tracker
from meltano.core.utils import get_no_color_flag

logger = logging.getLogger(__name__)


class NoWindowsGlobbingGroup(InstrumentedGroup):
    """A instrumented Click group that does not perform glob expansion on Windows.

    This restores the behaviour of Click's globbing to how it was before v8.
    Click (as of version 8.1.3) ignores quotes around an asterisk, which makes
    it behave differently than most shells that support globbing, and make some
    typical Meltano commands fail, e.g. `meltano select tap-gitlab tags "*"`.
    """

    def main(self, *args, **kwargs) -> NoReturn:
        """Invoke the Click CLI with Windows globbing disabled.

        Args:
            args: Positional arguments for the Click group.
            kwargs: Keyword arguments for the Click group.
        """
        return super().main(*args, windows_expand_args=False, **kwargs)


@click.group(
    cls=NoWindowsGlobbingGroup, invoke_without_command=True, no_args_is_help=True
)
@click.option("--log-level", type=click.Choice(LEVELS.keys()))
@click.option(
    "--log-config", type=str, help="Path to a python logging yaml config file."
)
@click.option("-v", "--verbose", count=True, help="Not used.")
@click.option(
    "--environment",
    envvar="MELTANO_ENVIRONMENT",
    help="Meltano environment name.",
)
@click.option(
    "--no-environment", is_flag=True, default=False, help="Don't use any environment."
)
@click.option(
    "--cwd",
    type=click.Path(exists=True, file_okay=False, resolve_path=True, path_type=Path),
    help="Run Meltano as if it had been started in the specified directory.",
)
@click.version_option(version=meltano.__version__, prog_name="meltano")
@click.pass_context
def cli(  # noqa: WPS231
    ctx: click.Context,
    log_level: str,
    log_config: str,
    verbose: int,
    environment: str,
    no_environment: bool,
    cwd: Path | None,
):  # noqa: WPS231
    """
    ELT for the DataOps era.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface
    """
    ctx.ensure_object(dict)

    if log_level:
        ProjectSettingsService.config_override["cli.log_level"] = log_level

    if log_config:
        ProjectSettingsService.config_override["cli.log_config"] = log_config

    ctx.obj["verbosity"] = verbose

    no_color = get_no_color_flag()
    if no_color:
        ctx.color = False

    if cwd:
        try:
            os.chdir(cwd)
        except OSError as ex:
            raise Exception(f"Unable to run Meltano from {cwd!r}") from ex

    try:  # noqa: WPS229
        project = Project.find()
        setup_logging(project)
        project_setting_service = ProjectSettingsService(project)

        readonly = project_setting_service.get("project_readonly")
        if readonly:
            project.readonly = True
        if project.readonly:
            logger.debug("Project is read-only.")

        # detect active environment
        selected_environment = None
        is_default_environment = False
        if no_environment or (environment and environment.lower() == "null"):
            logger.info("No environment is active")
        elif environment:
            selected_environment = environment
        elif project_setting_service.get("default_environment"):
            selected_environment = project_setting_service.get("default_environment")
            is_default_environment = True
        ctx.obj["selected_environment"] = selected_environment
        ctx.obj["is_default_environment"] = is_default_environment
        ctx.obj["project"] = project
        ctx.obj["tracker"] = Tracker(project)
        ctx.obj["tracker"].add_contexts(
            CliContext.from_click_context(ctx)
        )  # backfill the `cli` CliContext
    except ProjectNotFound:
        ctx.obj["project"] = None
    except IncompatibleVersionError:
        click.secho(
            "This Meltano project is incompatible with this version of `meltano`.",
            fg="yellow",
        )
        click.echo(
            "For more details, visit https://docs.meltano.com/guide/installation#upgrading-meltano-version"
        )
        sys.exit(3)


def activate_environment(
    ctx: click.Context, project: Project, required: bool = False
) -> None:
    """Activate the selected environment.

    The selected environment is whatever was selected with the `--environment`
    option, or the default environment (set in `meltano.yml`) otherwise.

    Args:
        ctx: The Click context, used to determine the selected environment.
        project: The project for which the environment will be activated.
    """
    if ctx.obj["selected_environment"]:
        project.activate_environment(ctx.obj["selected_environment"])
    elif required:
        raise MeltanoConfigurationError(
            reason="A Meltano environment must be specified",
            instruction="Set the `default_environment` option in "
            "`meltano.yml`, or the `--environment` CLI option",
        )


def activate_explicitly_provided_environment(
    ctx: click.Context, project: Project
) -> None:
    """Activate the selected environment if it has been explicitly set.

    Some commands (e.g. `config`, `job`, etc.) do not respect the configured
    `default_environment`, and will only run with an environment active if it
    has been explicitly set (e.g. with the `--environment` CLI option).

    Args:
        ctx: The Click context, used to determine the selected environment.
        project: The project for which the environment will be activated.
    """
    if ctx.obj["is_default_environment"]:
        logger.info(
            f"The default environment {ctx.obj['selected_environment']!r} will "
            f"be ignored for `meltano {ctx.command.name}`. To configure a specific "
            "environment, please use the option `--environment=<environment name>`."
        )
        project.deactivate_environment()
    else:
        activate_environment(ctx, project)
