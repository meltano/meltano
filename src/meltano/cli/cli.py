from __future__ import annotations

import logging  # noqa: D100
import sys
from typing import NoReturn

import click

import meltano
from meltano.cli.utils import InstrumentedGroup
from meltano.core.behavior.versioned import IncompatibleVersionError
from meltano.core.legacy_tracking import LegacyTracker
from meltano.core.logging import LEVELS, setup_logging
from meltano.core.project import Project, ProjectNotFound
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.tracking import CliContext, Tracker

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
@click.version_option(version=meltano.__version__, prog_name="meltano")
@click.pass_context
def cli(  # noqa: WPS231
    ctx,
    log_level: str,
    log_config: str,
    verbose: int,
    environment: str,
    no_environment: bool,
):  # noqa: WPS231
    """
    ELT for the DataOps era.

    \b\nRead more at https://www.meltano.com/docs/command-line-interface.html
    """
    ctx.ensure_object(dict)

    if log_level:
        ProjectSettingsService.config_override["cli.log_level"] = log_level

    if log_config:
        ProjectSettingsService.config_override["cli.log_config"] = log_config

    ctx.obj["verbosity"] = verbose
    try:  # noqa: WPS229
        project = Project.find()
        setup_logging(project)

        readonly = ProjectSettingsService(project).get("project_readonly")
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
        elif project.meltano.default_environment:
            selected_environment = project.meltano.default_environment
            is_default_environment = True
        # activate environment
        if selected_environment:
            project.activate_environment(selected_environment)
            logger.info(
                "Environment '%s' is active", selected_environment  # noqa: WPS323
            )
        ctx.obj["is_default_environment"] = is_default_environment
        ctx.obj["project"] = project
        ctx.obj["tracker"] = Tracker(project)
        ctx.obj["tracker"].add_contexts(
            CliContext.from_click_context(ctx)
        )  # backfill the `cli` CliContext
        ctx.obj["legacy_tracker"] = LegacyTracker(
            project, context_overrides=ctx.obj["tracker"].contexts
        )
    except ProjectNotFound:
        ctx.obj["project"] = None
    except IncompatibleVersionError:
        click.secho(
            "This Meltano project is incompatible with this version of `meltano`.",
            fg="yellow",
        )
        click.echo(
            "For more details, visit http://meltano.com/docs/installation.html#upgrading-meltano-version"
        )
        sys.exit(3)
