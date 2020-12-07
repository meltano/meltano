import pytest
import yaml

from meltano.core.meltano_file import MeltanoFile


class TestMeltanoFile:
    def test_load(self, project, tap, target):
        definition = project.meltano

        meltano_file = MeltanoFile.parse(project.meltano)
        assert meltano_file
