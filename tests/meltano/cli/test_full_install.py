import pytest
from unittest import mock

from meltano.cli import cli
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from asserts import assert_cli_runner


# Use One Class per End to End test in order to setup a new project each time
class TestFullInstall:
    @pytest.mark.slow
    @pytest.mark.backend("postgresql")
    def test_carbon_intensity_postgres_dbt(
        self, cli_runner, monkeypatch, project, elt_context_builder, project_add_service
    ):
        with mock.patch(
            "meltano.cli.add.ProjectAddService", return_value=project_add_service
        ), mock.patch(
            "meltano.cli.elt.ELTContextBuilder", return_value=elt_context_builder
        ):
            cli_args = ["add", "extractor", "tap-carbon-intensity"]
            result = cli_runner.invoke(cli, cli_args)
            assert_cli_runner(result)

            cli_args = ["add", "loader", "target-postgres"]
            result = cli_runner.invoke(cli, cli_args)
            assert_cli_runner(result)

            cli_args = ["add", "transformer", "dbt"]
            result = cli_runner.invoke(cli, cli_args)
            assert_cli_runner(result)

            cli_args = ["add", "model", "model-carbon-intensity"]
            result = cli_runner.invoke(cli, cli_args)
            assert_cli_runner(result)

            cli_args = [
                "elt",
                "tap-carbon-intensity",
                "target-postgres",
                "--transform",
                "run",
            ]

            result = cli_runner.invoke(cli, cli_args)
            assert_cli_runner(result)
