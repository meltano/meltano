import pytest

from meltano.cli import cli
from asserts import assert_cli_runner


# Use One Class per End to End test in order to setup a new project each time
class TestFullInstall:
    @pytest.mark.slow
    @pytest.mark.backend("postgresql")
    def test_carbon_intensity_postgres_dbt(request, cli_runner, monkeypatch, project):
        monkeypatch.setenv("PG_SCHEMA", "carbon")
        monkeypatch.setenv("PG_DATABASE", "pytest")
        monkeypatch.setenv("MELTANO_BACKEND", "postgresql")

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
