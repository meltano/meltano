from asynctest import mock

from meltano.core.block.ioblock import IOBlock
from meltano.core.block.parser import generate_job_id, is_command_block
from meltano.core.environment import Environment


class TestParserUtils:
    def test_is_command_block(self, tap, dbt):
        """Verify that the is_command_block function returns True when the block is an IOBlock and has a command."""
        assert not is_command_block(tap)
        assert is_command_block(dbt)

    def test_generate_job_id(self):
        """Verify that the job id is generated correctly when an environment is provided."""
        block1 = mock.Mock(spec=IOBlock)
        block1.string_id = "block1"

        block2 = mock.Mock(spec=IOBlock)
        block2.string_id = "block2"

        project = mock.Mock()

        project.active_environment = None
        assert not generate_job_id(project, block1, block2)

        project.active_environment = Environment(name="test")
        assert generate_job_id(project, block1, block2) == "test-block1-block2"
