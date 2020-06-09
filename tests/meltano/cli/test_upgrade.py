import yaml
import pytest
from unittest.mock import Mock, patch

from asserts import assert_cli_runner
from meltano.cli import cli


class TestCliUpgrade:
    def test_upgrade(self, cli_runner):
        result = cli_runner.invoke(cli, ["upgrade"])
        assert_cli_runner(result)

    def test_upgrade_skip_package(self, cli_runner):
        result = cli_runner.invoke(cli, ["upgrade", "--skip-package"])
        assert_cli_runner(result)

    def test_upgrade_package(self, cli_runner):
        result = cli_runner.invoke(cli, ["upgrade", "package"])
        assert_cli_runner(result)

    def test_upgrade_files(self, cli_runner):
        result = cli_runner.invoke(cli, ["upgrade", "files"])
        assert_cli_runner(result)

    def test_upgrade_database(self, cli_runner):
        result = cli_runner.invoke(cli, ["upgrade", "database"])
        assert_cli_runner(result)

    def test_upgrade_models(self, cli_runner):
        result = cli_runner.invoke(cli, ["upgrade", "models"])
        assert_cli_runner(result)
