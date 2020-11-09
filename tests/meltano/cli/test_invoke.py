import yaml
import json
import pytest
from unittest.mock import Mock, patch
from contextlib import contextmanager

from meltano.cli import cli
from meltano.core.project_add_service import ProjectAddService
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.plugin import PluginType
from meltano.core.plugin.singer import SingerTap
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.project import Project


@pytest.fixture(scope="class")
def project_add_service(project_add_service):
    project_add_service.add(PluginType.EXTRACTORS, "tap-mock")

    return project_add_service.project


@pytest.mark.usefixtures("project_add_service")
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
            assert invoke.called_once

    def test_invoke_args(self, cli_runner, process_mock):
        with patch.object(
            GoogleAnalyticsTracker, "track_data", return_value=None
        ), patch.object(PluginInvoker, "invoke", return_value=process_mock) as invoke:
            with_args = cli_runner.invoke(cli, ["invoke", "tap-mock", "--help"])

            assert invoke.called_with(["--help"])

    def test_invoke_exit_code(self, cli_runner, tap, process_mock):
        process_mock.wait.return_value = 2

        invoker_mock = Mock()
        invoker_mock.invoke.return_value = process_mock

        @contextmanager
        def prepared(session):
            yield

        invoker_mock.prepared = prepared

        with patch.object(
            GoogleAnalyticsTracker, "track_data", return_value=None
        ), patch("meltano.cli.invoke.invoker_factory", return_value=invoker_mock):
            basic = cli_runner.invoke(cli, ["invoke", tap.name])
            assert basic.exit_code == 2

    def test_invoke_dump_config(
        self, cli_runner, tap, plugin_discovery_service, plugin_settings_service_factory
    ):
        settings_service = plugin_settings_service_factory(tap)

        with patch.object(
            GoogleAnalyticsTracker, "track_data", return_value=None
        ), patch(
            "meltano.core.plugin_invoker.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), patch.object(
            SingerTap, "discover_catalog"
        ), patch.object(
            SingerTap, "apply_catalog_rules"
        ):
            result = cli_runner.invoke(cli, ["invoke", "--dump", "config", tap.name])

            assert json.loads(result.stdout) == settings_service.as_dict(
                extras=False, process=True
            )
