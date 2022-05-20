import responses

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.hub import MeltanoHubService
from meltano.core.plugin.base import PluginType


class TestCliDiscover:
    @responses.activate
    def test_discover(
        self,
        project,
        cli_runner,
        meltano_hub_service: MeltanoHubService,
        get_hub_response,
    ):
        extractors_url = meltano_hub_service.plugin_type_endpoint(PluginType.EXTRACTORS)
        loaders_url = meltano_hub_service.plugin_type_endpoint(PluginType.LOADERS)
        responses.add_callback(responses.GET, extractors_url, callback=get_hub_response)
        responses.add_callback(responses.GET, loaders_url, callback=get_hub_response)
        result = cli_runner.invoke(cli, ["discover"])
        assert_cli_runner(result)

        assert responses.assert_call_count(extractors_url, 1)
        assert responses.assert_call_count(loaders_url, 1)

        assert "Extractors" in result.output
        assert "tap-gitlab" in result.output
        assert "tap-mock" in result.output
        assert "tap-mock, variants: meltano (default), singer-io" in result.output

        assert "Loaders" in result.output
        assert "target-jsonl" in result.output
        assert "target-mock" in result.output

    @responses.activate
    def test_discover_extractors(
        self,
        project,
        cli_runner,
        meltano_hub_service: MeltanoHubService,
        get_hub_response,
    ):
        extractors_url = meltano_hub_service.plugin_type_endpoint(PluginType.EXTRACTORS)
        loaders_url = meltano_hub_service.plugin_type_endpoint(PluginType.LOADERS)
        responses.add_callback(responses.GET, extractors_url, callback=get_hub_response)
        result = cli_runner.invoke(cli, ["discover", "extractors"])
        assert_cli_runner(result)

        assert responses.assert_call_count(extractors_url, 1)
        assert responses.assert_call_count(loaders_url, 0)

        assert "Extractors" in result.output
        assert "tap-gitlab" in result.output
        assert "tap-mock" in result.output

        assert "Loaders" not in result.output
