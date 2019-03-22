import subprocess
import platform
from .project import Project
from .error import SubprocessError


class VenvService:
    def __init__(self, project):
        self.project = project

    def create(self, namespace="", name=""):
        venv_path = self.project.venvs_dir(namespace, name)
        if platform.system() == "Windows":
            python_executable = "python"
        else:
            python_executable = "python3"

        run = subprocess.run(
            [python_executable, "-m", "venv", str(venv_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        if run.returncode != 0:
            raise SubprocessError(
                f"Could not create of the virtualenv for '{namespace}/{name}'", run
            )

        return run

    def install(self, pip_url, namespace="", name=""):
        pip_install_path = self.exec_path("pip", namespace=namespace, name=name)

        run = subprocess.run(
            [str(pip_install_path), "install", *pip_url.split(" ")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        if run.returncode != 0:
            raise SubprocessError(f"Failed to install plugin '{name}'.", run)

        return run

    def exec_path(self, bin, name=None, namespace=""):
        name = name or bin
        if platform.system() == "Windows":
            exec_folder = "Scripts"
        else:
            exec_folder = "bin"
        return self.project.venvs_dir(namespace, name).joinpath(exec_folder, bin)
