import logging
import sys
import warnings

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
@click.version_option(version=meltano.__version__, prog_name="meltano")
@click.pass_context
def cli(  # noqa: WPS231
    ctx, log_level: str, log_config: str, verbose: int, environment: str
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

    try:
        project = Project.find()
        setup_logging(project)

        readonly = ProjectSettingsService(project).get("project_readonly")
        if readonly:
            project.readonly = True

        if project.readonly:
            logger.debug("Project is read-only.")

        if environment is not None:
            project.activate_environment(environment)
            logger.info("Environment '%s' is active", environment)  # noqa: WPS323

        ctx.obj["project"] = project
    except ProjectNotFound as err:
        ctx.obj["project"] = None
    except IncompatibleVersionError as err:
        click.secho(
            "This Meltano project is incompatible with this version of `meltano`.",
            fg="yellow",
        )
        click.echo(
            "For more details, visit http://meltano.com/docs/installation.html#upgrading-meltano-version"
        )
        sys.exit(3)
