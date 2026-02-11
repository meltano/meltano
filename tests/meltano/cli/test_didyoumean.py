from __future__ import annotations

from textwrap import dedent

import click
from click.testing import CliRunner

from meltano.cli._didyoumean import DYMGroup


class TestDYMGroup:
    def test_basic_functionality_with_group(self):
        @click.group(cls=DYMGroup)
        def cli(): ...

        @cli.command()
        def foo(): ...

        @cli.command()
        def bar(): ...

        @cli.command()
        def barrr(): ...

        runner = CliRunner()
        result = runner.invoke(cli, ["barr"])
        assert result.output == dedent(
            """\
            Usage: cli [OPTIONS] COMMAND [ARGS]...
            Try 'cli --help' for help.

            Error: No such command 'barr'.

            Did you mean one of these?
                barrr
                bar
            """
        )
