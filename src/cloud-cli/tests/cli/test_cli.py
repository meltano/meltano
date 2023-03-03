from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from meltano.cloud.cli import cloud as cli


def test_cli(tmp_path: Path):
    result = CliRunner().invoke(cli)
    assert "Interface with Meltano Cloud" in result.stdout
    assert result.exit_code == 0
