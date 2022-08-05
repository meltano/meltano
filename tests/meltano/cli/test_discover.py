from __future__ import annotations

from collections import Counter

import mock

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.hub import MeltanoHubService
from meltano.core.plugin.base import PluginType
from meltano.core.project import Project


class TestCliDiscover:
    def test_discover(
        self,
        project: Project,
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
            request_count = 1 if plugin_type.discoverable else 0
            assert hub_request_counter[f"/{plugin_type}/index"] == request_count

        assert "Extractors" in result.stdout
        assert "tap-gitlab" in result.stdout
        assert "tap-mock" in result.stdout
        assert "tap-mock, variants: meltano (default), singer-io" in result.stdout

        assert "Loaders" in result.stdout
        assert "target-jsonl" in result.stdout
        assert "target-mock" in result.stdout

    def test_discover_extractors(
        self,
        project: Project,
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

        assert "Extractors" in result.stdout
        assert "tap-gitlab" in result.stdout
        assert "tap-mock" in result.stdout

        assert "Loaders" not in result.stdout
