from __future__ import annotations

import os
import shutil
from functools import partial
from pathlib import Path

import pytest

from fixtures.utils import cd


@pytest.fixture(scope="class")
def compatible_copy_tree():
    """Copy files recursively from source to destination, ignoring existing dirs."""

    def _compatible_copy_tree(source: Path, destination: Path) -> None:
        """Copy files recursively from source to destination, ignoring existing dirs."""
        shutil.copytree(source, destination, dirs_exist_ok=True)

    return _compatible_copy_tree


@pytest.fixture
def function_scoped_test_dir(tmp_path_factory) -> Path:
    tmp_path = tmp_path_factory.mktemp("meltano_root")
    cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        yield tmp_path
    finally:
        os.chdir(cwd)


@pytest.fixture
def empty_meltano_yml_dir(tmp_path):
    with cd(tmp_path):
        (tmp_path / "meltano.yml").touch()
        return tmp_path


@pytest.fixture
def pushd(request):
    def _pushd(path):
        popd = partial(os.chdir, Path.cwd())
        request.addfinalizer(popd)
        os.chdir(path)

        return popd

    return _pushd
