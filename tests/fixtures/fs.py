from __future__ import annotations  # noqa: INP001

import os
import shutil
import typing as t
from functools import partial

import pytest

from fixtures.utils import cd

if t.TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture(scope="class")
def compatible_copy_tree():  # noqa: ANN201
    """Copy files recursively from source to destination, ignoring existing dirs."""

    def _compatible_copy_tree(source: Path, destination: Path):  # noqa: ANN202
        """Copy files recursively from source to destination, ignoring existing dirs."""
        shutil.copytree(source, destination, dirs_exist_ok=True)

    return _compatible_copy_tree


@pytest.fixture()
def function_scoped_test_dir(tmp_path_factory) -> Path:  # noqa: ANN001
    tmp_path = tmp_path_factory.mktemp("meltano_root")
    cwd = os.getcwd()  # noqa: PTH109
    try:
        os.chdir(tmp_path)
        yield tmp_path
    finally:
        os.chdir(cwd)


@pytest.fixture()
def empty_meltano_yml_dir(tmp_path):  # noqa: ANN001, ANN201
    with cd(tmp_path):
        (tmp_path / "meltano.yml").touch()
        return tmp_path


@pytest.fixture()
def pushd(request):  # noqa: ANN001, ANN201
    def _pushd(path):  # noqa: ANN001, ANN202
        popd = partial(os.chdir, os.getcwd())  # noqa: PTH109
        request.addfinalizer(popd)
        os.chdir(path)

        return popd

    return _pushd


@pytest.mark.meta()
def test_pushd(tmp_path, pushd):  # noqa: ANN001, ANN201
    os.makedirs(tmp_path / "a")  # noqa: PTH103
    os.makedirs(tmp_path / "a" / "b")  # noqa: PTH103

    pushd(tmp_path / "a")
    assert os.getcwd() == str(tmp_path / "a")  # noqa: PTH109

    popd = pushd("b")
    assert os.getcwd() == str(tmp_path / "a" / "b")  # noqa: PTH109

    popd()
    assert os.getcwd() == str(tmp_path / "a")  # noqa: PTH109
