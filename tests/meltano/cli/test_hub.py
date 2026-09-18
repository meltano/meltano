from __future__ import annotations

import json
import os
import time
import typing as t
from unittest import mock

import pytest
import requests
import requests_mock

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.hub.client import INDEX_CACHE_DURATION
from meltano.core.plugin import PluginType

if t.TYPE_CHECKING:
    from collections import Counter
    from pathlib import Path

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
            m.get(
                f"{hub_api}/plugins/orchestrators/index",
                exc=requests.exceptions.ConnectionError("Connection refused"),
            )
            result = cli_runner.invoke(cli, ("hub", "ping"))

        assert result.exit_code == 1
        assert "Could not connect to Meltano Hub at" in str(result.exception)
        assert not hub_request_counter

    def test_ping_unauthenticated(
        self,
        project: Project,
        cli_runner: CliRunner,
        hub_request_counter: Counter,
    ) -> None:
        hub_api = project.hub_service.hub_api_url
        with requests_mock.Mocker(session=project.hub_service.session) as m:
            m.get(
                f"{hub_api}/plugins/orchestrators/index",
                status_code=401,
                json={"message": "Meltano Hub requires a Meltano Cloud account."},
            )
            result = cli_runner.invoke(cli, ("hub", "ping"))

        assert result.exit_code == 1
        assert "Meltano Hub requires a Meltano Cloud account." in str(result.exception)
        assert "meltano cloud auth login" in str(result.exception)
        assert not hub_request_counter

    def test_ping_other_failure_is_still_wrapped(
        self,
        project: Project,
        cli_runner: CliRunner,
    ) -> None:
        hub_api = project.hub_service.hub_api_url
        with requests_mock.Mocker(session=project.hub_service.session) as m:
            m.get(
                f"{hub_api}/plugins/orchestrators/index",
                exc=ValueError("something else"),
            )
            result = cli_runner.invoke(cli, ("hub", "ping"))

        assert result.exit_code == 1
        assert f"Error: Failed to connect to the Hub at {hub_api!r}" in result.stderr


class TestCliHubList:
    @pytest.fixture(autouse=True)
    def cache_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
        """Give each test its own cache, so one cannot serve another."""
        path = tmp_path / "hub-index-cache"
        monkeypatch.setattr("meltano.core.hub.client.index_cache_dir", lambda: path)
        return path

    @staticmethod
    def invoke(project: Project, cli_runner: CliRunner, *args: str):
        with mock.patch(
            "requests.adapters.HTTPAdapter.send",
            project.hub_service.session.get_adapter(
                project.hub_service.hub_api_url,
            ).send,
        ):
            return cli_runner.invoke(cli, ("hub", "list", *args))

    def test_requires_a_cloud_account(
        self,
        project: Project,
        cli_runner: CliRunner,
    ) -> None:
        hub_api = project.hub_service.hub_api_url
        with requests_mock.Mocker(session=project.hub_service.session) as m:
            m.get(
                requests_mock.ANY,
                status_code=401,
                json={"message": "Meltano Hub requires a Meltano Cloud account."},
            )
            result = cli_runner.invoke(cli, ("hub", "list"))

        assert result.exit_code == 1
        # The gate is in the request, so this reads the same as 'hub ping',
        # 'meltano add' and 'meltano lock'.
        assert "Meltano Hub requires a Meltano Cloud account." in str(result.exception)
        assert "meltano cloud auth login" in str(result.exception)
        assert hub_api

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

    def test_a_pattern_matches_a_variant_name(
        self,
        project: Project,
        cli_runner: CliRunner,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        result = self.invoke(
            project, cli_runner, "singer-io", "--all", "--format", "json"
        )

        assert_cli_runner(result)
        entries = json.loads(result.stdout)
        # None of these plugins is named for the variant they share.
        assert {entry["variant"] for entry in entries} == {"singer-io"}
        assert "tap-mock" in {entry["name"] for entry in entries}

    def test_a_variant_matches_only_where_it_is_listed(
        self,
        project: Project,
        cli_runner: CliRunner,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        default_only = self.invoke(project, cli_runner, "singer-io", "--format", "json")
        every = self.invoke(
            project, cli_runner, "singer-io", "--all", "--format", "json"
        )

        assert_cli_runner(default_only)
        assert_cli_runner(every)
        # Without --all a plugin is listed on its default variant only, so a
        # plugin that merely offers this one is not among them.
        assert len(json.loads(default_only.stdout)) < len(json.loads(every.stdout))
        assert all(entry["default"] for entry in json.loads(default_only.stdout))

    def test_a_search_says_how_many_variants_it_left_out(
        self,
        project: Project,
        cli_runner: CliRunner,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        result = self.invoke(project, cli_runner, "singer-io")

        assert_cli_runner(result)
        # Two plugins are listed on this variant, and two more offer it
        # without defaulting to it.
        assert result.stdout.startswith(
            "2 plugins matching 'singer-io' (2 variants hidden, show with '--all')",
        )

    def test_one_variant_left_out_reads_as_one(
        self,
        project: Project,
        cli_runner: CliRunner,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        result = self.invoke(project, cli_runner, "gitlab")

        assert_cli_runner(result)
        assert "(1 variant hidden, show with '--all')" in result.stdout

    def test_nothing_is_left_out_when_every_variant_is_listed(
        self,
        project: Project,
        cli_runner: CliRunner,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        every = self.invoke(project, cli_runner, "singer-io", "--all")
        no_pattern = self.invoke(project, cli_runner)

        assert_cli_runner(every)
        assert_cli_runner(no_pattern)
        # Nothing is left out of --all, and a listing with no pattern leaves
        # out variants by design rather than by filtering.
        assert "hidden" not in every.stdout
        assert "hidden" not in no_pattern.stdout

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

    def test_caches_the_index(
        self,
        project: Project,
        cli_runner: CliRunner,
        cache_dir: Path,
        hub_request_counter: Counter,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        assert_cli_runner(
            self.invoke(project, cli_runner, "--plugin-type", "extractor")
        )
        assert hub_request_counter["/extractors/index"] == 1

        assert_cli_runner(
            self.invoke(project, cli_runner, "--plugin-type", "extractor")
        )
        # The second run reads what the first one wrote.
        assert hub_request_counter["/extractors/index"] == 1
        assert len(list(cache_dir.glob("*.json"))) == 1

    def test_refresh_fetches_and_replaces_what_was_cached(
        self,
        project: Project,
        cli_runner: CliRunner,
        cache_dir: Path,
        hub_request_counter: Counter,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        assert_cli_runner(
            self.invoke(project, cli_runner, "--plugin-type", "extractor")
        )
        assert hub_request_counter["/extractors/index"] == 1

        result = self.invoke(
            project, cli_runner, "--plugin-type", "extractor", "--refresh"
        )
        assert_cli_runner(result)
        assert hub_request_counter["/extractors/index"] == 2

        # What was fetched takes the place of what was cached, so the next run
        # is served the fresh copy rather than the one it replaced.
        assert_cli_runner(
            self.invoke(project, cli_runner, "--plugin-type", "extractor")
        )
        assert hub_request_counter["/extractors/index"] == 2
        assert len(list(cache_dir.glob("*.json"))) == 1

    def test_an_expired_index_is_fetched_again(
        self,
        project: Project,
        cli_runner: CliRunner,
        cache_dir: Path,
        hub_request_counter: Counter,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        assert_cli_runner(
            self.invoke(project, cli_runner, "--plugin-type", "extractor")
        )

        cached = next(iter(cache_dir.glob("*.json")))
        stale = time.time() - INDEX_CACHE_DURATION.total_seconds() - 1
        os.utime(cached, (stale, stale))

        assert_cli_runner(
            self.invoke(project, cli_runner, "--plugin-type", "extractor")
        )
        assert hub_request_counter["/extractors/index"] == 2

    def test_the_cache_is_keyed_by_plugin_type(
        self,
        project: Project,
        cli_runner: CliRunner,
        cache_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")
        assert_cli_runner(
            self.invoke(project, cli_runner, "--plugin-type", "extractor")
        )
        assert_cli_runner(self.invoke(project, cli_runner, "--plugin-type", "loader"))

        assert len(list(cache_dir.glob("*.json"))) == 2
