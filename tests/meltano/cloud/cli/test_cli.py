from __future__ import annotations

from click.testing import CliRunner

from meltano.cloud.cli import cloud as cli


def test_cli():
    result = CliRunner().invoke(cli)
    assert "Interface with Meltano Cloud" in result.stdout
    assert result.exit_code == 0
