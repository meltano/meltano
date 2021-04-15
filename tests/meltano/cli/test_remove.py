from unittest import mock

from asserts import assert_cli_runner
from meltano.cli import cli


class TestCliRemove:
    def test_remove(self, project, tap, cli_runner):
        with mock.patch("meltano.cli.remove.remove_plugins") as remove_plugin_mock:
            result = cli_runner.invoke(cli, ["remove", tap.type, tap.name])
            assert_cli_runner(result)

            remove_plugin_mock.assert_called_once_with(project, [tap])
