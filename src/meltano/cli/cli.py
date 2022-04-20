import logging  # noqa: D100
import sys
import warnings  # noqa: F401

import click

import meltano
from meltano.core.behavior.versioned import IncompatibleVersionError
from meltano.core.logging import LEVELS, setup_logging
from meltano.core.project import Project, ProjectNotFound
from meltano.core.project_settings_service import ProjectSettingsService

logger = logging.getLogger(__name__)


@click.group(invoke_without_command=True, no_args_is_help=True)
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
    if log_level:
        ProjectSettingsService.config_override["cli.log_level"] = log_level

    if log_config:
        ProjectSettingsService.config_override["cli.log_config"] = log_config

    ctx.ensure_object(dict)
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
        if no_environment or (environment and environment.lower() == "null"):
            logger.info("No environment is active")
        elif environment:
            selected_environment = environment
        elif project.meltano.default_environment:
            selected_environment = project.meltano.default_environment
        # activate environment
        if selected_environment:
            project.activate_environment(selected_environment)
            logger.info(
                "Environment '%s' is active", selected_environment  # noqa: WPS323
            )

        ctx.obj["project"] = project
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
