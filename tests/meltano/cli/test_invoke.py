import json
from contextlib import contextmanager
from unittest.mock import Mock, patch

import pytest
import yaml
from meltano.cli import cli
from meltano.core.plugin import PluginType
from meltano.core.plugin.singer import SingerTap
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.project import Project
from meltano.core.tracking import GoogleAnalyticsTracker


@pytest.fixture(scope="class")
def project_tap_mock(project_add_service):
    return project_add_service.add(PluginType.EXTRACTORS, "tap-mock")


@pytest.mark.usefixtures("project_tap_mock")
class TestCliInvoke:
    @pytest.fixture
    def process_mock(self):
        process_mock = Mock()
        process_mock.wait.return_value = 0

        return process_mock

    def test_invoke(self, cli_runner, process_mock):
        with patch.object(
            GoogleAnalyticsTracker, "track_data", return_value=None
        ), patch.object(PluginInvoker, "invoke", return_value=process_mock) as invoke:
            basic = cli_runner.invoke(cli, ["invoke", "tap-mock"])
            invoke.assert_called_once

    def test_invoke_args(self, cli_runner, process_mock):
        with patch.object(
            GoogleAnalyticsTracker, "track_data", return_value=None
        ), patch.object(PluginInvoker, "invoke", return_value=process_mock) as invoke:
            with_args = cli_runner.invoke(cli, ["invoke", "tap-mock", "--help"])

            invoke.assert_called_with(["--help"])

    def test_invoke_exit_code(
        self, cli_runner, tap, process_mock, project_plugins_service
    ):
        process_mock.wait.return_value = 2

        invoker_mock = Mock()
        invoker_mock.invoke.return_value = process_mock

        @contextmanager
        def prepared(session):
            yield

        invoker_mock.prepared = prepared

        with patch.object(
            GoogleAnalyticsTracker, "track_data", return_value=None
        ), patch(
            "meltano.cli.invoke.ProjectPluginsService",
            return_value=project_plugins_service,
        ), patch(
            "meltano.cli.invoke.invoker_factory", return_value=invoker_mock
        ):
            basic = cli_runner.invoke(cli, ["invoke", tap.name])
            assert basic.exit_code == 2

    def test_invoke_dump_config(
        self, cli_runner, tap, project_plugins_service, plugin_settings_service_factory
    ):
        settings_service = plugin_settings_service_factory(tap)

        with patch.object(
            GoogleAnalyticsTracker, "track_data", return_value=None
        ), patch(
            "meltano.cli.invoke.ProjectPluginsService",
            return_value=project_plugins_service,
        ), patch.object(
            SingerTap, "discover_catalog"
        ), patch.object(
            SingerTap, "apply_catalog_rules"
        ):
            result = cli_runner.invoke(cli, ["invoke", "--dump", "config", tap.name])

            assert json.loads(result.stdout) == settings_service.as_dict(
                extras=False, process=True
            )
