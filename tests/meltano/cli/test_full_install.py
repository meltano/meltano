import pytest

from click.testing import CliRunner

from meltano.cli import cli


# Use One Class per End to End test in order to setup a new project each time
class TestFullInstall:
    @pytest.mark.slow
    def test_carbon_intensity_postgres_dbt(request, project):
        # Manually add the extractor, loader and dbt before running the elt command
        cli_runner = CliRunner()

        cli_args = ["add", "extractor", "tap-carbon-intensity"]
        result = cli_runner.invoke(cli, cli_args)
        assert result.exit_code == 0

        cli_args = ["add", "loader", "target-postgres"]
        result = cli_runner.invoke(cli, cli_args)
        assert result.exit_code == 0

        cli_args = ["add", "transformer", "dbt"]
        result = cli_runner.invoke(cli, cli_args)
        assert result.exit_code == 0

        cli_args = [
            "elt",
            "tap-carbon-intensity",
            "target-postgres",
            "--transform",
            "run",
        ]
        result = cli_runner.invoke(cli, cli_args)
        assert result.exit_code == 0
