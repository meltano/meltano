import subprocess
from .project import Project


class VenvService:
    def __init__(self, project):
        self.project = project

    def create(self, namespace="", name=""):
        venv_path = self.project.venvs_dir(namespace, name)
        run_venv = subprocess.run(
            ["python3", "-m", "venv", venv_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        return {"stdout": run_venv.stdout, "stderr": run_venv.stderr}

    def install(self, pip_url, namespace="", name=""):
        pip_install_path = self.exec_path("pip", namespace=namespace, name=name)
        run_pip_install = subprocess.run(
            [pip_install_path, "install", *pip_url.split(" ")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        return {"stdout": run_pip_install.stdout, "stderr": run_pip_install.stderr}

    def exec_path(self, bin, name=None, namespace=""):
        name = name or bin
        return self.project.venvs_dir(namespace, name).joinpath("bin", bin)
