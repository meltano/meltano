import yaml
import pytest
from unittest.mock import Mock, patch

from meltano.cli import cli
from meltano.core.project_add_service import ProjectAddService
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.plugin import PluginType
from meltano.core.tracking import GoogleAnalyticsTracker


class TestCliInvoke:
    @pytest.fixture
    def subject(self, cli_runner, project_add_service, config_service):
        project_add_service.add(PluginType.EXTRACTORS, "tap-mock")

        return cli_runner

    @pytest.fixture
    def process_mock(self):
        process_mock = Mock()
        process_mock.wait.return_value = 0

        return process_mock

    def test_invoke(self, subject, process_mock):
        with patch.object(
            GoogleAnalyticsTracker, "track_data", return_value=None
        ), patch.object(PluginInvoker, "invoke", return_value=process_mock) as invoke:
            basic = subject.invoke(cli, ["invoke", "tap-mock"])
            assert invoke.called_once

    def test_invoke_args(self, subject, process_mock):
        with patch.object(
            GoogleAnalyticsTracker, "track_data", return_value=None
        ), patch.object(PluginInvoker, "invoke", return_value=process_mock) as invoke:
            with_args = subject.invoke(cli, ["invoke", "tap-mock", "--discover"])

            assert invoke.called_with(["--discover"])

    def test_invoke_exit_code(self, subject, process_mock):
        process_mock.wait.return_value = 2

        with patch.object(
            GoogleAnalyticsTracker, "track_data", return_value=None
        ), patch.object(PluginInvoker, "invoke", return_value=process_mock) as invoke:
            basic = subject.invoke(cli, ["invoke", "tap-mock"])
            assert basic.exit_code == 2
