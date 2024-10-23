from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.meta
def test_pushd(tmp_path: Path, pushd):
    tmp_path.joinpath("a").mkdir(parents=True)
    tmp_path.joinpath("a", "b").mkdir(parents=True)

    pushd(tmp_path / "a")
    assert Path.cwd() == tmp_path / "a"

    popd = pushd("b")
    assert Path.cwd() == tmp_path / "a" / "b"

    popd()
    assert Path.cwd() == tmp_path / "a"
