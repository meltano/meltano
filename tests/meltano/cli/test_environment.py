from __future__ import annotations

import typing as t

import pytest

from meltano.cli import cli

if t.TYPE_CHECKING:
    from click.testing import CliRunner


class TestEnvironment:
    @pytest.mark.order(0)
    @pytest.mark.usefixtures("project")
    def test_add(self, cli_runner: CliRunner):
        """Test ``meltano environment add``."""
        result = cli_runner.invoke(cli, ("environment", "add", "foo"))
        assert result.exit_code == 0, result.stdout

    @pytest.mark.order(1)
    @pytest.mark.usefixtures("project")
    def test_list_environments(self, cli_runner: CliRunner):
        """Test ``meltano environment list``."""
        result = cli_runner.invoke(cli, ("environment", "list"))
        assert result.exit_code == 0, result.stdout
        assert "foo" in result.stdout

    @pytest.mark.order(2)
    @pytest.mark.usefixtures("project")
    def test_remove(self, cli_runner: CliRunner):
        """Test ``meltano environment remove``."""
        result = cli_runner.invoke(cli, ("environment", "remove", "foo"))
        assert result.exit_code == 0, result.stdout
