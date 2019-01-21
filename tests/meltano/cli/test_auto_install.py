import pytest

from click.testing import CliRunner

from meltano.cli import cli


class TestAutoInstall:
    @pytest.mark.slow
    def test_carbon_intensity_sqlite(request, project):
        # Directly run `meltano add loader target-sqlite` in a new project
        # So that the extractor and the loader are auto installed by meltano
        cli_runner = CliRunner()

        cli_args = ["elt", "tap-carbon-intensity", "target-sqlite"]
        result = cli_runner.invoke(cli, cli_args)
        assert result.exit_code == 0
