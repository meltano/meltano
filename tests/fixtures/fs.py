import os
import shutil
import sys
import tempfile
from distutils import dir_util
from functools import partial
from pathlib import Path

import pytest


@pytest.fixture(scope="class")
def compatible_copy_tree():
    """Copy files recursively from source to destination, ignoring existing dirs."""
    # noqa: DAR201
    def _compatible_copy_tree(source: Path, destination: Path):
        """Copy files recursively from source to destination, ignoring existing dirs."""
        if sys.version_info >= (3, 8):
            # shutil.copytree option `dirs_exist_ok` was added in python3.8
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            dir_util.copy_tree(str(source), str(destination))

    return _compatible_copy_tree


@pytest.fixture(scope="function")
def mkdtemp(request):
    def _mkdtemp(*args, **kwargs):
        path = Path(tempfile.mkdtemp())
        cleanup = partial(shutil.rmtree, path, ignore_errors=True)

        request.addfinalizer(cleanup)
        return path

    return _mkdtemp


@pytest.fixture(scope="session")
def test_dir(tmp_path_factory):
    cwd = os.getcwd()
    test_dir = tmp_path_factory.mktemp("meltano_root")

    try:  # noqa: WPS229
        os.chdir(test_dir)
        yield test_dir
    finally:
        os.chdir(cwd)
        shutil.rmtree(test_dir)


@pytest.fixture
def pushd(request):
    def _pushd(path):
        popd = partial(os.chdir, os.getcwd())
        request.addfinalizer(popd)
        os.chdir(path)

        return popd

    return _pushd


@pytest.mark.meta
def test_pushd(mkdtemp, pushd):
    temp = mkdtemp()

    os.makedirs(temp.joinpath("a"))
    os.makedirs(temp.joinpath("a/b"))

    pushd(temp / "a")
    assert os.getcwd() == str(temp.joinpath("a"))

    popd = pushd("b")
    assert os.getcwd() == str(temp.joinpath("a/b"))

    popd()
    assert os.getcwd() == str(temp.joinpath("a"))
