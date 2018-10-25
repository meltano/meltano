import subprocess
from .project import Project


class VenvService:
    def __init__(self, project):
        self.project = project

    def create(self, namespace="", name=""):
        venv_path = self.project.venvs_dir(namespace, name)
        run_venv = subprocess.run(
            ["virtualenv", venv_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        return {"stdout": run_venv.stdout, "stderr": run_venv.stderr}

    def install(self, pip_url, namespace="", name=""):
        pip_install_path = self.project.venvs_dir(namespace, name, "bin", "pip")
        run_pip_install = subprocess.run(
            [pip_install_path, "install", pip_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        return {"stdout": run_pip_install.stdout, "stderr": run_pip_install.stderr}
