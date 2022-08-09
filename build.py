from __future__ import annotations

import os
import shutil
import subprocess


def build():
    # Build static web app
    subprocess.run(["yarn", "install", "--immutable"], cwd="src/webapp")
    subprocess.run(["yarn", "build"], cwd="src/webapp")

    # Copy static files
    os.makedirs("src/meltano/api/templates", exist_ok=True)
    shutil.copy(
        "src/webapp/dist/index.html",
        "src/meltano/api/templates/webapp.html",
    )
    shutil.copy(
        "src/webapp/dist/index-embed.html",
        "src/meltano/api/templates/embed.html",
    )

    for dst in {"css", "js"}:
        shutil.rmtree(f"src/meltano/api/static/{dst}", ignore_errors=True)
        shutil.copytree(
            f"src/webapp/dist/static/{dst}",
            f"src/meltano/api/static/{dst}",
        )


if __name__ == "__main__":
    build()
