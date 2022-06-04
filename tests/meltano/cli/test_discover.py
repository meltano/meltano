from collections import Counter
from unittest import mock

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.hub import MeltanoHubService
from meltano.core.plugin.base import PluginType


class TestCliDiscover:
    def test_discover(
        self,
        project,
        cli_runner,
        meltano_hub_service: MeltanoHubService,
        hub_request_counter: Counter,
    ):
        adapter = meltano_hub_service.session.get_adapter(
            meltano_hub_service.hub_api_url
        )

        with mock.patch("requests.adapters.HTTPAdapter.send", adapter.send):
            result = cli_runner.invoke(cli, ["discover"])

        assert_cli_runner(result)

        for plugin_type in PluginType:
            assert hub_request_counter[f"/{plugin_type}/index"] == 1

        assert "Extractors" in result.output
        assert "tap-gitlab" in result.output
        assert "tap-mock" in result.output
        assert "tap-mock, variants: meltano (default), singer-io" in result.output

        assert "Loaders" in result.output
        assert "target-jsonl" in result.output
        assert "target-mock" in result.output

    def test_discover_extractors(
        self,
        project,
        cli_runner,
        meltano_hub_service: MeltanoHubService,
        hub_request_counter: Counter,
    ):
        adapter = meltano_hub_service.session.get_adapter(
            meltano_hub_service.hub_api_url,
        )

        with mock.patch("requests.adapters.HTTPAdapter.send", adapter.send):
            result = cli_runner.invoke(cli, ["discover", "extractors"])

        assert_cli_runner(result)

        assert hub_request_counter["/extractors/index"] == 1
        assert hub_request_counter["/loaders/index"] == 0

        assert "Extractors" in result.output
        assert "tap-gitlab" in result.output
        assert "tap-mock" in result.output

        assert "Loaders" not in result.output
