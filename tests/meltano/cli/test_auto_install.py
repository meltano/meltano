from __future__ import annotations

import pytest

from asserts import assert_cli_runner
from meltano.cli import cli


class TestAutoInstall:
    @pytest.mark.slow
    @pytest.mark.skip(reason="Deadlock on docker, have to investigate further.")
    def test_carbon_intensity_sqlite(self, cli_runner, monkeypatch, project):
        # Directly run `meltano add loader target-sqlite` in a new project
        # So that the extractor and the loader are auto installed by meltano
        cli_args = ["elt", "tap-carbon-intensity", "target-sqlite"]
        result = cli_runner.invoke(cli, cli_args)

        assert_cli_runner(result)
