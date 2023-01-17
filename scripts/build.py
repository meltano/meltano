"""A PEP 517 build backend for Meltano.

This uses the PEP 517 build backend provided by `poetry-core`, with a slight
modification. The `WheelBuilder.build` method has been patched to allow us to
make arbitrary changes to the source/sdist immediately prior to the
construction of the wheel.

This is used instead of Poetry's unofficial `build.py` approach because Poetry
the assumes that if `build.py` is used, it should build a platform-specific
wheel, rather than a platform-agnostic pure wheel.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from warnings import warn


def build_webapp() -> None:
    """Build the Meltano UI webapp."""
    warning_prefix = "Failed to build Meltano UI webapp:"

    try:
        node_version_check = subprocess.run(
            ("node", "--version"), text=True, capture_output=True
        )
        node_version_check.check_returncode()
    except Exception:
        warn(f"{warning_prefix} could not execute 'node --version'", Warning)
        return

    try:
        subprocess.run(("yarn", "--version")).check_returncode()
    except Exception:
        warn(f"{warning_prefix} could not execute 'yarn --version'", Warning)
        return

    if not node_version_check.stdout.startswith("v16"):
        warn(f"{warning_prefix} NodeJS v16 is required", Warning)
        return

    # Build static web app
    subprocess.run(("yarn", "install", "--immutable"), cwd="src/webapp")
    subprocess.run(("yarn", "build"), cwd="src/webapp")


def include_webapp() -> None:
    """Copy the built webapp into the source tree."""
    os.makedirs("src/meltano/api/templates", exist_ok=True)
    shutil.copy(
        "src/webapp/dist/index.html",
        "src/meltano/api/templates/webapp.html",
    )
    shutil.copy(
        "src/webapp/dist/index-embed.html",
        "src/meltano/api/templates/embed.html",
    )
    for dst in ("css", "js"):
        shutil.rmtree(f"src/meltano/api/static/{dst}", ignore_errors=True)
        shutil.copytree(
            f"src/webapp/dist/static/{dst}",
            f"src/meltano/api/static/{dst}",
        )


def include_schemas() -> None:
    """Copy Meltano schemas into the source tree."""
    shutil.rmtree("src/meltano/schema/", ignore_errors=True)
    shutil.copytree("schema/", "src/meltano/schema/")
    # TODO: Once Python 3.7 support is dropped, we should use
    #       `shutil.copytree(..., dirs_exist_ok=True)` instead of deleting the
    #       directory first.


from poetry.core.masonry.builders.wheel import WheelBuilder  # noqa: E402

original_wheel_build = WheelBuilder.build


def custom_build_wheel(*args, **kwargs) -> str:
    """Wheel building via poetry-core with customizations for Meltano.

    Args:
        args: Positional arguments to pass through to `WheelBuilder.build`.
        kwargs: Keyword arguments to pass through to `WheelBuilder.build`.

    Returns:
        The value returned by `WheelBuilder.build(*args, **kwargs)`.
    """
    build_webapp()
    include_webapp()
    include_schemas()
    return original_wheel_build(*args, **kwargs)


WheelBuilder.build = custom_build_wheel

# Provide the Poetry core PEP 517 API, which will now use the patched `WheelBuilder`.
from poetry.core.masonry import api  # noqa: F401, E402
