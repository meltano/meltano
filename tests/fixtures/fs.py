import os
import shutil
import tempfile
from functools import partial
from pathlib import Path

import pytest


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

    try:
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
    cwd = os.getcwd()

    os.makedirs(temp.joinpath("a"))
    os.makedirs(temp.joinpath("a/b"))

    pushd(temp / "a")
    assert os.getcwd() == str(temp.joinpath("a"))

    popd = pushd("b")
    assert os.getcwd() == str(temp.joinpath("a/b"))

    popd()
    assert os.getcwd() == str(temp.joinpath("a"))
