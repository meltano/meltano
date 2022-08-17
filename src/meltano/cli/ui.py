"""Meltano UI CLI."""

from __future__ import annotations

import logging
import os
import secrets
import signal

import click

from meltano.api.workers import APIWorker, UIAvailableWorker
from meltano.cli import cli
from meltano.cli.params import pass_project
from meltano.cli.utils import CliError, InstrumentedCmd, InstrumentedDefaultGroup
from meltano.core.project import Project
from meltano.core.project_settings_service import (
    ProjectSettingsService,
    SettingValueStore,
)

logger = logging.getLogger(__name__)


def ensure_secure_setup(project: Project):
    """Verify UI security settings."""
    settings_service = ProjectSettingsService(project)

    if not settings_service.get("ui.authentication"):
        return

    facts = []
    if (
        settings_service.get("ui.server_name") is None
        and settings_service.get("ui.session_cookie_domain") is None
    ):
        facts.append(
            "- Neither the 'ui.server_name' or 'ui.session_cookie_domain' setting has been set"
        )

    secure_settings = ["ui.secret_key", "ui.password_salt"]
    for setting_name in secure_settings:
        value, source = settings_service.get_with_source(setting_name)
        if source is SettingValueStore.DEFAULT:
            facts.append(
                f"- The '{setting_name}' setting has not been changed from the default test value"
            )

    if facts:
        click.secho(
            "Authentication is enabled, but your configuration is currently insecure:",
            fg="red",
        )
        for fact in facts:
            click.echo(fact)
        click.echo(
            "For more information about these settings and how to set them, visit "
            "https://docs.meltano.com/reference/settings#uiauthentication"
        )
        click.echo()


def start_workers(workers):
    """Start UI background workers."""

    def stop_all():
        logger.info("Stopping all background workers...")
        for worker in workers:
            worker.stop()

    # start all workers
    for worker in workers:
        worker.start()

    return stop_all


@cli.group(
    cls=InstrumentedDefaultGroup,
    default="start",
    default_if_no_args=True,
    short_help="Start the Meltano UI webserver.",
)
@pass_project(migrate=True)
@click.pass_context
def ui(ctx, project: Project):
    """
    Start the Meltano UI webserver.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#ui
    """
    ctx.obj["project"] = project


@ui.command(cls=InstrumentedCmd, short_help="Start the Meltano UI webserver.")
@click.option("--reload", is_flag=True, default=False)
@click.option("--bind", help="The hostname (or IP address) to bind on")
@click.option("--bind-port", help="Port to run webserver on", type=int)
@click.pass_context
def start(ctx, reload, bind, bind_port):
    """Start the Meltano UI webserver."""
    if bind:
        ProjectSettingsService.config_override["ui.bind_host"] = bind
    if bind_port:
        ProjectSettingsService.config_override["ui.bind_port"] = bind_port

    project: Project = ctx.obj["project"]
    ensure_secure_setup(project)

    workers = []

    workers.append(UIAvailableWorker(project))
    workers.append(
        APIWorker(project, reload=reload or os.getenv("FLASK_ENV") == "development")
    )

    cleanup = start_workers(workers)

    def handle_terminate(signal, frame):  # noqa: WPS442
        cleanup()

    signal.signal(signal.SIGTERM, handle_terminate)
    logger.info("All workers started.")


@ui.command(
    cls=InstrumentedCmd, short_help="Generate and store server name and secrets."
)
@click.argument("server_name")
@click.option(
    "--bits",
    default=256,  # noqa: WPS432
    help="Specify the size of secrets in bits in the system DB (default 256)",
)
@click.pass_context
def setup(ctx, server_name, **flags):
    """
    Generate and store server name and secrets.

    WARNING\n
        Regenerating secrets will cause the following:

        - All passwords will be invalid\n
        - All sessions will be expired\n

    Use with caution!
    """
    project = ctx.obj["project"]
    settings_service = ProjectSettingsService(project)

    def set_setting_env(setting_name, value):
        settings_service.set(setting_name, value, store=SettingValueStore.DOTENV)

    set_setting_env("ui.server_name", server_name)

    ui_cfg_path = project.root_dir("ui.cfg")
    if ui_cfg_path.exists():
        raise CliError(
            f"Found existing secrets in file '{ui_cfg_path}'. Please delete this file and rerun this command to regenerate the secrets."
        )

    def generate_secret():
        return secrets.token_hex(int(flags["bits"] / 8))  # in bytes

    secret_settings = ["ui.secret_key", "ui.password_salt"]
    for setting_name in secret_settings:
        value, source = settings_service.get_with_source(setting_name)
        if source is not SettingValueStore.DEFAULT:
            click.echo(
                f"Setting '{setting_name}' has already been set in {source.label}. Please unset it manually and rerun this command to regenerate this secret."
            )
        else:
            set_setting_env(setting_name, generate_secret())

    click.echo(
        "The server name and generated secrets have been stored in your project's `.env` file."
    )
    click.echo(
        "In production, you will likely want to move these settings to actual environment variables, since `.env` is in `.gitignore` by default."
    )
