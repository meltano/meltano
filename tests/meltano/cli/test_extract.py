import pytest
import os
from unittest.mock import patch
from functools import partial

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.runner.singer import SingerRunner
from meltano.core.runner.dbt import DbtRunner
from meltano.core.dbt_service import DbtService
from meltano.core.tracking import GoogleAnalyticsTracker


@pytest.mark.backend("sqlite")
@patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
def test_elt(
    google_tracker,
    cli_runner,
    project,
    tap,
    target,
    plugin_settings_service,
    plugin_discovery_service,
):
    result = cli_runner.invoke(cli, ["elt"])
    assert result.exit_code == 2

    args = ["elt", tap.name, target.name]

    # exit cleanly when everything is fine
    # fmt: off
    with patch.object(SingerRunner, "run", return_value=None), \
      patch("meltano.cli.elt.install_missing_plugins", return_value=None), \
      patch("meltano.core.elt_context.PluginDiscoveryService", return_value=plugin_discovery_service), \
      patch("meltano.core.elt_context.PluginSettingsService", return_value=plugin_settings_service):
        result = cli_runner.invoke(cli, args)
        assert_cli_runner(result)
    # fmt: on

    # aborts when there is an exception
    with patch("meltano.cli.elt.install_missing_plugins", return_value=None):
        result = cli_runner.invoke(cli, args)
        assert result.exit_code == 1

    with patch.object(SingerRunner, "run", side_effect=Exception):
        result = cli_runner.invoke(cli, args)
        assert result.exit_code == 1


@pytest.mark.backend("sqlite")
@patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
def test_elt_transform_only(
    google_tracker,
    cli_runner,
    project,
    tap,
    target,
    plugin_discovery_service,
    plugin_settings_service,
):
    # exit cleanly when `meltano elt ... --transform only` runs for
    # a tap with no default transforms

    args = ["elt", tap.name, target.name, "--transform", "only"]

    # fmt: off
    with patch("meltano.core.runner.dbt.DbtService", autospec=True) as DbtService, \
      patch("meltano.cli.elt.add_plugin", return_value=None) as add_plugin, \
      patch("meltano.core.elt_context.PluginDiscoveryService", return_value=plugin_discovery_service), \
      patch("meltano.core.elt_context.PluginSettingsService", return_value=plugin_settings_service), \
      patch.object(DbtRunner, "run", return_value=None):
        dbt_service = DbtService.return_value

        result = cli_runner.invoke(cli, args)
        assert_cli_runner(result)

        dbt_service.deps.assert_called
        add_plugin.assert_called
    # fmt: on
