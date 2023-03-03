from __future__ import annotations

from click.testing import CliRunner

from meltano.cloud.cli import cloud as cli


def test_cli(tmp_path: Path):
    result = CliRunner().invoke(cli, ["--config-path", tmp_path / "meltano-cloud.json"])
    assert result.exit_code == 0
