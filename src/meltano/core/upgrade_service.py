import os
import click
import logging
import psutil
import importlib
import meltano
import subprocess
import signal
import shutil
from typing import Optional

from meltano.core.project import Project
from meltano.core.migration_service import MigrationService, MigrationError
from meltano.core.config_service import ConfigService
from meltano.cli.utils import install_plugins, PluginInstallReason
from meltano.core.compiler.project_compiler import ProjectCompiler
import meltano.core.bundle as bundle


class UpgradeError(Exception):
    """Occurs when the Meltano upgrade fails"""

    pass


class AutomaticPackageUpgradeError(Exception):
    def __init__(self, reason, instructions):
        self.reason = reason
        self.instructions = instructions


class UpgradeService:
    def __init__(self, engine, project: Project):
        self.project = project
        self.engine = engine

    def reload_ui(self):
        click.secho("Reloading UI...", fg="blue")

        pid_file_path = self.project.run_dir("gunicorn.pid")
        try:
            with pid_file_path.open("r") as pid_file:
                pid = int(pid_file.read())

                process = psutil.Process(pid)
                process.send_signal(signal.SIGHUP)
        except FileNotFoundError:
            click.echo("UI is not running")
        except Exception as ex:
            logging.error(f"Cannot restart from `{pid_file_path}`: {ex}")

    def _upgrade_package(self, pip_url: Optional[str] = None, force=False):
        meltano_file_path = "/src/meltano/__init__.py"
        editable = meltano.__file__.endswith(meltano_file_path)
        if editable and not force:
            meltano_dir = meltano.__file__[0 : -len(meltano_file_path)]
            raise AutomaticPackageUpgradeError(
                reason="it is installed from source",
                instructions=f"navigate to `{meltano_dir}` and run `git pull`",
            )

        in_docker = os.path.exists("/.dockerenv")
        if in_docker:
            raise AutomaticPackageUpgradeError(
                reason="it is installed inside Docker",
                instructions="pull the latest Docker image using `docker pull meltano/meltano` and recreate any containers you may have created",
            )

        pip_url = pip_url or "meltano"
        run = subprocess.run(
            ["pip", "install", "--upgrade", pip_url],
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        if run.returncode != 0:
            raise UpgradeError(f"Failed to upgrade `meltano`.", run)

        return True

    def upgrade_package(self, *args, **kwargs):
        click.secho("Upgrading `meltano` package...", fg="blue")

        try:
            self._upgrade_package(*args, **kwargs)
            click.echo("The `meltano` package has been upgraded.")

            click.echo()
            self.reload_ui()

            return True
        except AutomaticPackageUpgradeError as err:
            click.echo(
                f"{click.style('The `meltano` package could not be upgraded automatically', fg='red')} because {err.reason}."
            )
            click.echo(f"To upgrade manually, {err.instructions}.")
            return False

    def update_files(self):
        """
        Update the files managed by Meltano inside the current project.
        """
        click.secho("Updating files managed by plugins...", fg="blue")

        file_plugins = ConfigService(self.project).get_files()
        if not file_plugins:
            click.echo("Nothing to update")
            return

        install_plugins(self.project, file_plugins, reason=PluginInstallReason.UPGRADE)

    def migrate_database(self):
        click.secho("Applying migrations to system database...", fg="blue")

        try:
            migration_service = MigrationService(self.engine)
            migration_service.upgrade()
            migration_service.seed(self.project)
        except MigrationError as err:
            raise UpgradeError(str(err)) from err

    def compile_models(self):
        click.secho("Recompiling models...", fg="blue")

        ProjectCompiler(self.project).compile()

    def upgrade(self, skip_package=False, **kwargs):
        package_upgraded = False
        if not skip_package:
            package_upgraded = self.upgrade_package(**kwargs)

            if not package_upgraded:
                click.echo(
                    "Then, run `meltano upgrade --skip-package` to upgrade your project based on the latest version."
                )
                return

            click.echo()

        self.update_files()
        click.echo()
        self.migrate_database()
        click.echo()
        self.compile_models()

        click.echo()
        if package_upgraded:
            click.secho(
                "Meltano and your Meltano project have been upgraded!", fg="green"
            )
        else:
            click.secho("Your Meltano project has been upgraded!", fg="green")
