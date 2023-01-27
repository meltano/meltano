from __future__ import annotations

import mock
import pytest

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.plugin import PluginType
from meltano.core.project_add_service import PluginAlreadyAddedException


class TestCliRemove:
    @pytest.fixture(scope="class")
    def tap_gitlab(self, project_add_service):
        try:
            return project_add_service.add(PluginType.EXTRACTORS, "tap-gitlab")
        except PluginAlreadyAddedException as err:
            return err.plugin

    def test_remove(self, project, tap, cli_runner):
        with mock.patch("meltano.cli.remove.remove_plugins") as remove_plugins_mock:
            result = cli_runner.invoke(cli, ["remove", tap.type, tap.name])
            assert_cli_runner(result)

            remove_plugins_mock.assert_called_once_with(project, [tap])

    def test_remove_multiple(self, project, tap, tap_gitlab, cli_runner):
        with mock.patch("meltano.cli.remove.remove_plugins") as remove_plugins_mock:
            result = cli_runner.invoke(
                cli, ["remove", "extractors", tap.name, tap_gitlab.name]
            )
            assert_cli_runner(result)

            remove_plugins_mock.assert_called_once_with(project, [tap, tap_gitlab])

    def test_remove_type_name(self, project, tap, target, cli_runner):
        with mock.patch("meltano.cli.remove.remove_plugins") as remove_plugins_mock:
            result = cli_runner.invoke(cli, ["remove", "extractor", tap.name])
            assert_cli_runner(result)

            remove_plugins_mock.assert_called_with(project, [tap])

            result = cli_runner.invoke(cli, ["remove", "loader", target.name])
            assert_cli_runner(result)

            remove_plugins_mock.assert_called_with(project, [target])

            assert remove_plugins_mock.call_count == 2
