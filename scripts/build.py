#!/usr/bin/env python

"""Build script for Meltano wheels that builds and bundles the Meltano UI.

This script is run automatically by Poetry when building a wheel.

It can also be run manually for the purpose of UI development.
"""

import os
import shutil
import subprocess
from pathlib import Path

root_dir = Path(__file__).parent.parent.resolve()
webapp_dir = root_dir / "src" / "webapp"
dist_dir = webapp_dir / "dist"
api_dir = root_dir / "src" / "meltano" / "api"


def build():
    """Build & bundle the Meltano UI - executed automatically by Poetry when building the wheel."""
    # Operate from the root of the project
    os.chdir(root_dir)

    # Build static web app
    subprocess.run(["yarn", "install", "--immutable"], cwd=webapp_dir)  # noqa: S607
    subprocess.run(["yarn", "build"], cwd=webapp_dir)  # noqa: S607

    # Copy static files
    os.makedirs(api_dir / "templates", exist_ok=True)
    shutil.copy(dist_dir / "index.html", api_dir / "templates" / "webapp.html")
    shutil.copy(dist_dir / "index-embed.html", api_dir / "templates" / "embed.html")

    for dst in ("css", "js"):
        shutil.rmtree(api_dir / "static" / dst, ignore_errors=True)
        shutil.copytree(dist_dir / "static" / dst, api_dir / "static" / dst)


if __name__ == "__main__":
    build()
