#!/usr/bin/env python

"""Check that subproject deps are included by the root project.

This script that checks that the root project (Meltano) includes all of the
dependencies used by its subprojects. Its subprojects (e.g. the Meltano Cloud
CLI) have their own dependencies, and can be installed separately. When Meltano
is installed it includes each subprocess, and so must have all of their
dependencies too.

Some manual work must be done to keep the various `pyproject.toml` files
in-sync, but this script prevents them from going out of sync - it's impossible
to neglect to keep them in-sync unless you ignore the pre-commit CI checks.

Hopefully in the future Poetry will have more built-in capabilities to handle
monorepos.
"""

from __future__ import annotations

import argparse
import sys
import typing as t
from os import PathLike
from pathlib import Path

import tomli

repo_root_path = Path(__file__).parent.parent


def normalize_dep(dep: tuple[str, str | dict[str, str | bool]]) -> str:
    """Normalize dependencies from `pyproject.toml` into a string identifier.

    Args:
        dep: A dependency taken directly from the parsed `pyproject.toml` file.

    Returns:
        A string which identifies the dependency name, along with all other
        relevant info that should be matched by the root dependencies.
    """
    name, info = dep
    version: str = info["version"] if isinstance(info, dict) else info
    return f"{name} {version}"


def deps_from_pyproject_toml(pyproject_toml_path: PathLike) -> set[str]:
    """Extract all normalized main dependencies from a path to a `pyproject.toml` file.

    Args:
        pyproject_toml_path: The path to a `pyproject.toml` file.

    Returns:
        The normalized main dependencies, i.e. excluding dev dependencies.
    """
    with open(pyproject_toml_path, "rb") as pyproject_toml_file:
        pyproject_toml = tomli.load(pyproject_toml_file)
    # NOTE: This only works for Projects using Poetry's `pyproject.toml` format
    return {
        normalize_dep(dep)
        for dep in pyproject_toml["tool"]["poetry"]["dependencies"].items()
    }


def check_subproject_deps(
    root_pyproject_toml_path: PathLike,
    subproject_pyproject_toml_paths: t.Sequence[PathLike],
) -> None:
    """Check that every subproject dep is included by the root project.

    Args:
        root_pyproject_toml_path: Path to the root project `pyproject.toml` file.
        subproject_pyproject_toml_paths: Paths to subproject `pyproject.toml` files.

    Raises:
        Exception: Checked subprojects have dependencies missing from the root
            project.
    """
    root_deps = deps_from_pyproject_toml(root_pyproject_toml_path)
    for subproject_pyproject_toml in subproject_pyproject_toml_paths:
        subproject_deps = deps_from_pyproject_toml(subproject_pyproject_toml)
        missing_deps = subproject_deps - root_deps
        if missing_deps:
            raise Exception(
                f"Subproject defined at '{subproject_pyproject_toml}' has dependencies "
                f"missing from the root 'pyproject.toml': {missing_deps!r}"
            )


def main(argv: t.Sequence[str] | None = None) -> int:
    """Run the script to check that subproject deps are included by the root project.

    Args:
        argv: Command line arguments. They should specify the path to the
            `pyproject.toml` files belonging to subprojects being checked.

    Returns:
        0 if all subproject deps are included by the root project; 1 otherwise.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args(argv)

    try:
        check_subproject_deps(repo_root_path / "pyproject.toml", args.filenames)
    except Exception as ex:
        print(ex, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
