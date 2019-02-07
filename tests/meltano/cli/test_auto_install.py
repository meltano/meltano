import pytest
from click.testing import CliRunner

from meltano.cli import cli
from asserts import assert_cli_runner


class TestAutoInstall:
    @pytest.mark.slow
    def test_carbon_intensity_sqlite(request, db, monkeypatch, project):
        monkeypatch.setenv("PG_SCHEMA", "carbon")
        monkeypatch.setenv("PG_DATABASE", "pytest")

        # Directly run `meltano add loader target-sqlite` in a new project
        # So that the extractor and the loader are auto installed by meltano
        cli_runner = CliRunner()

        cli_args = ["elt", "tap-carbon-intensity", "target-sqlite"]
        result = cli_runner.invoke(cli, cli_args)

        assert_cli_runner(result)
