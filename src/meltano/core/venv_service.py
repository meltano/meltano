import subprocess
import platform
import sys
import os
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

        # we want the plugin to inherit our current venv
        sys_paths = []
        for path in sys.path:
            if path.endswith("site-packages"):
                sys_paths.append(path)
            if path.endswith("meltano/src"):  # meltano is installed as editable
                sys_paths.append(path)

        # inject a .pth to include the current virtualenv if possible
        meltano_pth_path = venv_path.joinpath(
            "lib", "python" + sys.version[:3], "site-packages", "meltano_venv.pth"
        )
        with meltano_pth_path.open("w") as pth:
            for path in sys_paths:
                pth.write(path + "\n")

        return run

    def install(self, pip_url, namespace="", name=""):
        pip_install_path = self.exec_path("pip", namespace=namespace, name=name)

        # we run `pip install ... --ignore-installed` to make sure the plugin
        # install ALL its dependencies, even if Meltano could provide some via
        # its own virtualenv
        run = subprocess.run(
            [
                str(pip_install_path),
                "install",
                *pip_url.split(" "),
                "--ignore-installed",
            ],
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
