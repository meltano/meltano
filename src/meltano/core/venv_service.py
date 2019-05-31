import subprocess
import platform
import sys
import os
from abc import ABC
from .project import Project
from .error import SubprocessError


VenvSpecs = namedtuple("VenvSpecs", (
    "python_executable",
    "lib_dir",
    "bin_dir",
    "site_packages_dir")
)


class VenvProvider(ABC):
    PLATFORM_SPECS = {
        "Linux": VenvSpecs(
            lib_dir="lib",
            bin_dir="bin",
            site_packages_dir=os.path.join("python", sys.version[:3], "site-packages"),
            python_executable="python3",
        ),
        "Windows": VenvSpecs(
            lib_dir="Lib",
            bin_dir="Scripts",
            site_packages_dir="site-packages",
            python_executable="python"
        ),
    }

    def __init__(self, root: Path):
        self.root = root
        self._specs = self.__class__.platform_specs()

    @classmethod
    def platform_specs(cls):
        try:
            system = platform.system()
            return self.__class__.PLATFORM_SPECS[system]
        except KeyError:
            raise Exception(f"Platform {system} not supported.")

    def __getattribute__(self, attr):
        return self._specs[attr]


class VenvService:
    def __init__(self, project):
        self.project = project

    def create(self, namespace="", name=""):
        venv_path = self.project.venvs_dir(namespace, name)
        provider = VenvProvider(venv_path)

        run = subprocess.run(
            [provider.python_executable, "-m", "venv", str(venv_path)],
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

            if path.endswith(os.path.join("meltano", "src")):  # meltano is installed as editable
                sys_paths.append(path)

        # inject a .pth to include the current virtualenv if possible
        meltano_pth_path = venv_path.joinpath(
            provider.site_packages_dir, "meltano_venv.pth"
        )
        with meltano_pth_path.open("w") as pth:
            for path in sys_paths:
                pth.write(path + os.linesep)

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
        venv = VirtualEnv(self.project.venvs_dir(namespace, name))
        return venv.bin_dir(bin)
