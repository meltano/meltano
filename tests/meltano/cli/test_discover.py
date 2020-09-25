import pytest
from unittest import mock

from asserts import assert_cli_runner
from meltano.cli import cli


class TestCliDiscover:
    def test_discover(self, project, cli_runner, plugin_discovery_service):
        with mock.patch(
            "meltano.cli.discovery.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ):
            result = cli_runner.invoke(cli, ["discover"])
            assert_cli_runner(result)

            assert "Extractors" in result.output
            assert "tap-gitlab" in result.output
            assert (
                "tap-mock, variants: meltano (default), singer-io (deprecated)"
                in result.output
            )

            assert "Loaders" in result.output
            assert "target-jsonl" in result.output
            assert "target-mock" in result.output

    def test_discover_extractors(self, project, cli_runner, plugin_discovery_service):
        with mock.patch(
            "meltano.cli.discovery.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ):
            result = cli_runner.invoke(cli, ["discover", "extractors"])
            assert_cli_runner(result)

            assert "Extractors" in result.output
            assert "tap-gitlab" in result.output
            assert "tap-mock" in result.output

            assert "Loaders" not in result.output
