from __future__ import annotations

from meltano.cli import cli
from click.testing import CliRunner
from asserts import assert_cli_runner


class TestCliLogin:
    def test_login(self, cli_runner: CliRunner):
        result = cli_runner.invoke(cli, ["login"])
        assert_cli_runner(result)
