from __future__ import annotations

import os
import shutil
import sys
from distutils import dir_util
from functools import partial
from pathlib import Path

import pytest

from fixtures.utils import cd


@pytest.fixture(scope="class")
def compatible_copy_tree():
    """Copy files recursively from source to destination, ignoring existing dirs."""

    def _compatible_copy_tree(source: Path, destination: Path):
        """Copy files recursively from source to destination, ignoring existing dirs."""
        if sys.version_info >= (3, 8):
            # shutil.copytree option `dirs_exist_ok` was added in python3.8
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            dir_util.copy_tree(str(source), str(destination))

    return _compatible_copy_tree


@pytest.fixture()
def function_scoped_test_dir(tmp_path_factory) -> Path:
    tmp_path = tmp_path_factory.mktemp("meltano_root")
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        yield tmp_path
    finally:
        os.chdir(cwd)


@pytest.fixture()
def empty_meltano_yml_dir(tmp_path):
    with cd(tmp_path):
        (tmp_path / "meltano.yml").touch()
        return tmp_path


@pytest.fixture()
def pushd(request):
    def _pushd(path):
        popd = partial(os.chdir, os.getcwd())
        request.addfinalizer(popd)
        os.chdir(path)

        return popd

    return _pushd


@pytest.mark.meta()
def test_pushd(tmp_path, pushd):
    os.makedirs(tmp_path / "a")
    os.makedirs(tmp_path / "a" / "b")

    pushd(tmp_path / "a")
    assert os.getcwd() == str(tmp_path / "a")

    popd = pushd("b")
    assert os.getcwd() == str(tmp_path / "a" / "b")

    popd()
    assert os.getcwd() == str(tmp_path / "a")
