from __future__ import annotations

import json
import typing as t
from unittest import mock

import requests_mock

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.plugin import PluginType

if t.TYPE_CHECKING:
    from collections import Counter

    import pytest
    from click.testing import CliRunner

    from meltano.core.project import Project


class TestCliHub:
    def test_ping(
        self,
        project: Project,
        cli_runner: CliRunner,
        hub_request_counter: Counter,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        with mock.patch(
            "requests.adapters.HTTPAdapter.send",
            project.hub_service.session.get_adapter(
                project.hub_service.hub_api_url,
            ).send,
        ):
            result = cli_runner.invoke(cli, ("hub", "ping"))

        assert_cli_runner(result)

        assert hub_request_counter["/orchestrators/index"] == 1
        assert (
            f"Successfully connected to the Hub at {project.hub_service.hub_api_url!r}"
            in result.stdout
        )

    def test_ping_unreachable(
        self,
        project: Project,
        cli_runner: CliRunner,
        hub_request_counter: Counter,
    ) -> None:
        hub_api = project.hub_service.hub_api_url
        with requests_mock.Mocker(session=project.hub_service.session) as m:
            m.get(hub_api, exc=ConnectionError("Connection refused"))
            result = cli_runner.invoke(cli, ("hub", "ping"))

        assert result.exit_code == 1
        assert f"Error: Failed to connect to the Hub at {hub_api!r}" in result.stderr
        assert not hub_request_counter


class TestCliHubList:
    @staticmethod
    def invoke(project: Project, cli_runner: CliRunner, *args: str):
        with mock.patch(
            "requests.adapters.HTTPAdapter.send",
            project.hub_service.session.get_adapter(
                project.hub_service.hub_api_url,
            ).send,
        ):
            return cli_runner.invoke(cli, ("hub", "list", *args))

    def test_lists_every_discoverable_type(
        self,
        project: Project,
        cli_runner: CliRunner,
        hub_request_counter: Counter,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        result = self.invoke(project, cli_runner)

        assert_cli_runner(result)
        assert "tap-google-analytics" in result.stdout
        assert "target-mock" in result.stdout
        # A mapping is not indexed, so it costs no request.
        for plugin_type in PluginType:
            expected = 1 if plugin_type.discoverable else 0
            assert hub_request_counter[f"/{plugin_type}/index"] == expected

    def test_limits_to_one_plugin_type(
        self,
        project: Project,
        cli_runner: CliRunner,
        hub_request_counter: Counter,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        result = self.invoke(project, cli_runner, "--plugin-type", "extractor")

        assert_cli_runner(result)
        assert "tap-google-analytics" in result.stdout
        assert "target-mock" not in result.stdout
        assert hub_request_counter["/extractors/index"] == 1
        assert hub_request_counter["/loaders/index"] == 0

    def test_json_output(
        self,
        project: Project,
        cli_runner: CliRunner,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        result = self.invoke(
            project, cli_runner, "--plugin-type", "extractor", "--format", "json"
        )

        assert_cli_runner(result)
        entries = {entry["name"]: entry for entry in json.loads(result.stdout)}
        entry = entries["tap-google-analytics"]
        assert entry["type"] == "extractor"
        assert entry["variant"] == "meltanolabs"
        assert entry["default"] is True

    def test_lists_the_default_variant_only(
        self,
        project: Project,
        cli_runner: CliRunner,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        result = self.invoke(
            project,
            cli_runner,
            "--plugin-type",
            "extractor",
            "--format",
            "json",
        )

        assert_cli_runner(result)
        entries = json.loads(result.stdout)
        # tap-gitlab offers two variants, and only its default is listed.
        gitlab = [entry for entry in entries if entry["name"] == "tap-gitlab"]
        assert [entry["variant"] for entry in gitlab] == ["meltanolabs"]
        assert all(entry["default"] for entry in entries)

    def test_all_lists_every_variant(
        self,
        project: Project,
        cli_runner: CliRunner,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        result = self.invoke(
            project,
            cli_runner,
            "--plugin-type",
            "extractor",
            "--all",
            "--format",
            "json",
        )

        assert_cli_runner(result)
        entries = json.loads(result.stdout)
        gitlab = [entry for entry in entries if entry["name"] == "tap-gitlab"]
        # The default comes first, and the rest follow it.
        assert [entry["variant"] for entry in gitlab] == ["meltanolabs", "meltano"]
        assert [entry["default"] for entry in gitlab] == [True, False]

    def test_marks_the_default_only_when_listing_every_variant(
        self,
        project: Project,
        cli_runner: CliRunner,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        default_only = self.invoke(project, cli_runner, "--plugin-type", "extractor")
        every = self.invoke(project, cli_runner, "--plugin-type", "extractor", "--all")

        assert_cli_runner(default_only)
        assert_cli_runner(every)
        # Every row is the default when only defaults are listed, so saying so
        # on each of them would tell the reader nothing.
        assert "(default)" not in default_only.stdout
        assert "(default)" in every.stdout

    def test_a_lone_variant_is_not_marked_as_the_default(
        self,
        project: Project,
        cli_runner: CliRunner,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        result = self.invoke(project, cli_runner, "--plugin-type", "extractor", "--all")

        assert_cli_runner(result)
        lines = result.stdout.splitlines()
        # tap-carbon-intensity offers one variant, and tap-gitlab two.
        carbon = next(line for line in lines if "tap-carbon-intensity" in line)
        gitlab = next(line for line in lines if "tap-gitlab" in line)
        assert "(default)" not in carbon
        assert "(default)" in gitlab

    def test_a_pattern_matches_anywhere_in_a_name(
        self,
        project: Project,
        cli_runner: CliRunner,
        hub_request_counter: Counter,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        result = self.invoke(project, cli_runner, "GITLAB", "--format", "json")

        assert_cli_runner(result)
        names = [entry["name"] for entry in json.loads(result.stdout)]
        # The match ignores case, and matches anywhere in the name.
        assert names == ["tap-gitlab"]
        # Filtering happens here, so it still costs a request for each type.
        assert hub_request_counter["/extractors/index"] == 1

    def test_a_pattern_that_matches_nothing(
        self,
        project: Project,
        cli_runner: CliRunner,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        result = self.invoke(project, cli_runner, "no-such-plugin", "--format", "json")

        assert_cli_runner(result)
        assert json.loads(result.stdout) == []

    def test_counts_the_results_above_the_table(
        self,
        project: Project,
        cli_runner: CliRunner,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        one = self.invoke(project, cli_runner, "gitlab")
        every = self.invoke(project, cli_runner, "--plugin-type", "extractor", "--all")

        assert_cli_runner(one)
        assert_cli_runner(every)
        # The count is singular where it should be, and names what a row is.
        assert one.stdout.startswith("1 plugin matching 'gitlab'")
        assert every.stdout.startswith("14 extractor variants")

    def test_a_plugin_is_named_once_however_many_variants_it_has(
        self,
        project: Project,
        cli_runner: CliRunner,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        text = self.invoke(project, cli_runner, "gitlab", "--all")
        data = self.invoke(project, cli_runner, "gitlab", "--all", "--format", "json")

        assert_cli_runner(text)
        assert_cli_runner(data)
        # tap-gitlab takes two rows, and is named on the first of them only.
        assert text.stdout.count("tap-gitlab") == 1
        # The JSON is read by a machine, so every record names its plugin.
        entries = json.loads(data.stdout)
        assert [entry["name"] for entry in entries] == ["tap-gitlab", "tap-gitlab"]
        assert all(entry["type"] == "extractor" for entry in entries)

    def test_the_count_names_the_plugin_type(
        self,
        project: Project,
        cli_runner: CliRunner,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        none = self.invoke(project, cli_runner, "f1", "--plugin-type", "extractor")
        one = self.invoke(project, cli_runner, "mock", "--plugin-type", "loader")
        bundles = self.invoke(project, cli_runner, "--plugin-type", "file")

        assert_cli_runner(none)
        assert_cli_runner(one)
        assert_cli_runner(bundles)
        assert none.stdout.strip() == "0 extractors matching 'f1'"
        assert one.stdout.startswith("1 loader matching 'mock'")
        # A file bundle is two words, and pluralises on the second.
        assert bundles.stdout.startswith("3 file bundles")

    def test_no_table_when_nothing_matches(
        self,
        project: Project,
        cli_runner: CliRunner,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        result = self.invoke(project, cli_runner, "no-such-plugin")

        assert_cli_runner(result)
        assert result.stdout.strip() == "0 plugins matching 'no-such-plugin'"
        assert "NAME" not in result.stdout

    def test_names_are_sorted(
        self,
        project: Project,
        cli_runner: CliRunner,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        result = self.invoke(
            project, cli_runner, "--plugin-type", "extractor", "--format", "json"
        )

        assert_cli_runner(result)
        names = [entry["name"] for entry in json.loads(result.stdout)]
        assert names == sorted(names)
