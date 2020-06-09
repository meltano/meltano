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
from meltano.core.migration_service import MigrationService
import meltano.core.compiler.project_compiler
import meltano.core.bundle as bundle


class UpgradeError(Exception):
    """Occurs when the Meltano upgrade fails"""

    pass


class UpgradeService:
    def __init__(
        self, engine, project: Project, migration_service: MigrationService = None
    ):
        self.project = project
        self.migration_service = migration_service or MigrationService(engine)

    def reload_ui(self):
        click.secho("Reloading UI if running...", fg="blue")

        pid_file_path = self.project.run_dir("gunicorn.pid")
        try:
            with pid_file_path.open("r") as pid_file:
                pid = int(pid_file.read())

                process = psutil.Process(pid)
                process.send_signal(signal.SIGHUP)
        except FileNotFoundError:
            pass
        except Exception as ex:
            logging.error(f"Cannot restart from `{pid_file_path}`: {ex}")

    def _upgrade_package(self, pip_url: Optional[str] = None, force=False):
        meltano_file_path = "/src/meltano/__init__.py"
        editable = meltano.__file__.endswith(meltano_file_path)
        editable = editable and not force
        if editable:
            meltano_dir = meltano.__file__[0 : -len(meltano_file_path)]
            click.echo(
                f"{click.style('The `meltano` package could not be upgraded automatically', fg='red')} because it is installed from source."
            )
            click.echo(
                f"To upgrade manually, navigate to `{meltano_dir}` and run `git pull`."
            )
            return False

        in_docker = os.path.exists("/.dockerenv")
        if in_docker:
            click.echo(
                f"{click.style('The `meltano` package could not be upgraded automatically', fg='red')} because it is installed inside Docker."
            )
            click.echo(
                f"To upgrade manually, pull the latest Docker image using `docker pull meltano/meltano` and recreate any containers you may have created."
            )
            return False

        pip_url = pip_url or "meltano"
        run = subprocess.run(
            ["pip", "install", "--upgrade", pip_url],
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        if run.returncode != 0:
            raise UpgradeError(f"Failed to upgrade `meltano`.", run)

        click.echo("The `meltano` package has been upgraded.")
        return True

    def upgrade_package(self, *args, **kwargs):
        click.secho("Upgrading `meltano` package...", fg="blue")
        package_upgraded = self._upgrade_package(*args, **kwargs)

        if not package_upgraded:
            click.echo(
                "Then, run `meltano upgrade --skip-package` to upgrade your project based on the latest version."
            )
        else:
            self.reload_ui()

        return package_upgraded

    def update_files(self):
        """
        Update the files managed by Meltano inside the current project.
        """
        click.secho("Updating files managed by plugins...", fg="blue")

        files_map = {
            bundle.find("dags/meltano.py"): self.project.root_dir(
                "orchestrate/dags/meltano.py"
            ),
            bundle.find("transform/profile/profiles.yml"): self.project.root_dir(
                "transform/profile/profiles.yml"
            ),
        }

        for src, dst in files_map.items():
            try:
                shutil.copy(src, dst)
                click.echo(f"Updated {dst}")
            except Exception as err:
                logging.error(f"Meltano could not update {dst}: {err}")

    def migrate_database(self):
        click.secho("Applying migrations to system database...", fg="blue")
        self.migration_service.upgrade()
        self.migration_service.seed(self.project)

    def compile_models(self):
        click.secho("Recompiling models...", fg="blue")

        # Make sure we load the _new_ Meltano version's ProjectCompiler
        importlib.reload(meltano.core.compiler.project_compiler)
        from meltano.core.compiler.project_compiler import ProjectCompiler

        ProjectCompiler(self.project).compile()

    def upgrade(self, skip_package=False, **kwargs):
        package_upgraded = False
        if not skip_package:
            package_upgraded = self.upgrade_package(**kwargs)

            if not package_upgraded:
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
