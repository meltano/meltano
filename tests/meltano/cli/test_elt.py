import pytest
import os
import logging
from unittest import mock
from functools import partial

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.project_add_service import PluginAlreadyAddedException
from meltano.core.plugin import PluginType, PluginRef
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.plugin.dbt import DbtPlugin
from meltano.core.runner.singer import SingerRunner
from meltano.core.runner.dbt import DbtRunner
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.job import Job


@pytest.fixture(scope="class")
def tap_mock_transform(project_add_service):
    try:
        return project_add_service.add(PluginType.TRANSFORMS, "tap-mock-transform")
    except PluginAlreadyAddedException as err:
        return err.plugin


class TestCliEltScratchpadOne:
    @pytest.mark.backend("sqlite")
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    def test_elt_missing_plugins(
        self, google_tracker, cli_runner, project, plugin_discovery_service
    ):
        args = ["elt", "tap-mock", "target-mock"]

        with mock.patch(
            "meltano.cli.elt.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), mock.patch(
            "meltano.core.elt_context.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), mock.patch.object(
            SingerRunner, "run", return_value=None
        ), mock.patch(
            "meltano.cli.elt.install_plugins", return_value=True
        ) as install_plugin_mock:
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            install_plugin_mock.assert_called_once_with(
                project,
                [
                    PluginRef(PluginType.LOADERS, "target-mock"),
                    PluginRef(PluginType.EXTRACTORS, "tap-mock"),
                ],
                reason=PluginInstallReason.ADD,
            )

    @pytest.mark.backend("sqlite")
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    def test_elt(
        self,
        google_tracker,
        cli_runner,
        project,
        tap,
        target,
        plugin_discovery_service,
        job_logging_service,
    ):
        result = cli_runner.invoke(cli, ["elt"])
        assert result.exit_code == 2

        job_id = "pytest_test_elt"
        args = ["elt", "--job_id", job_id, tap.name, target.name]

        # exit cleanly when everything is fine
        with mock.patch.object(SingerRunner, "run", return_value=None), mock.patch(
            "meltano.cli.elt.install_plugins", return_value=True
        ) as install_plugin_mock, mock.patch(
            "meltano.core.elt_context.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ):

            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            install_plugin_mock.assert_not_called()

        # aborts when there is an exception
        with mock.patch("meltano.cli.elt.install_missing_plugins", return_value=None):
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1

        job_logging_service.delete_all_logs(job_id)

        with mock.patch.object(
            SingerRunner, "run", side_effect=Exception("This is a grave danger.")
        ), mock.patch(
            "meltano.core.elt_context.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ):
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1

            # ensure there is a log of this exception
            log = job_logging_service.get_latest_log(job_id)
            assert "This is a grave danger.\n" in log


class TestCliEltScratchpadTwo:
    @pytest.mark.backend("sqlite")
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    def test_elt_transform_run_missing_plugins(
        self, google_tracker, cli_runner, project, plugin_discovery_service
    ):
        args = ["elt", "tap-mock", "target-mock", "--transform", "run"]

        with mock.patch(
            "meltano.cli.elt.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), mock.patch(
            "meltano.core.elt_context.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), mock.patch(
            "meltano.core.transform_add_service.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), mock.patch.object(
            SingerRunner, "run", return_value=None
        ), mock.patch.object(
            DbtRunner, "run", return_value=None
        ), mock.patch(
            "meltano.cli.elt.install_plugins", return_value=True
        ) as install_plugin_mock:
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            install_plugin_mock.assert_called_once_with(
                project,
                [
                    PluginRef(PluginType.FILES, "dbt"),
                    PluginRef(PluginType.TRANSFORMERS, "dbt"),
                    PluginRef(PluginType.TRANSFORMS, "tap-mock-transform"),
                    PluginRef(PluginType.LOADERS, "target-mock"),
                    PluginRef(PluginType.EXTRACTORS, "tap-mock"),
                ],
                reason=PluginInstallReason.ADD,
            )

    @pytest.mark.backend("sqlite")
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    def test_elt_transform_run(
        self,
        google_tracker,
        cli_runner,
        project,
        tap,
        target,
        dbt,
        tap_mock_transform,
        plugin_discovery_service,
    ):
        args = ["elt", tap.name, target.name, "--transform", "run"]

        with mock.patch(
            "meltano.cli.elt.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), mock.patch(
            "meltano.core.elt_context.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), mock.patch(
            "meltano.core.transform_add_service.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), mock.patch.object(
            SingerRunner, "run", return_value=None
        ), mock.patch.object(
            DbtRunner, "run", return_value=None
        ), mock.patch(
            "meltano.cli.elt.install_plugins", return_value=True
        ) as install_plugin_mock:
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            install_plugin_mock.assert_not_called()


class TestCliEltScratchpadThree:
    @pytest.mark.backend("sqlite")
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    def test_elt_transform_only_missing_plugins(
        self, google_tracker, cli_runner, project, tap, target, plugin_discovery_service
    ):
        args = ["elt", tap.name, target.name, "--transform", "only"]

        with mock.patch(
            "meltano.cli.elt.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), mock.patch(
            "meltano.core.elt_context.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), mock.patch(
            "meltano.core.transform_add_service.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), mock.patch.object(
            DbtRunner, "run", return_value=None
        ), mock.patch(
            "meltano.cli.elt.install_plugins", return_value=True
        ) as install_plugin_mock:
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            install_plugin_mock.assert_called_once_with(
                project,
                [
                    PluginRef(PluginType.FILES, "dbt"),
                    PluginRef(PluginType.TRANSFORMERS, "dbt"),
                    PluginRef(PluginType.TRANSFORMS, "tap-mock-transform"),
                ],
                reason=PluginInstallReason.ADD,
            )

    @pytest.mark.backend("sqlite")
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    def test_elt_transform_only(
        self,
        google_tracker,
        cli_runner,
        project,
        tap,
        target,
        dbt,
        tap_mock_transform,
        plugin_discovery_service,
    ):
        args = ["elt", tap.name, target.name, "--transform", "only"]

        with mock.patch(
            "meltano.cli.elt.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), mock.patch(
            "meltano.core.elt_context.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), mock.patch(
            "meltano.core.transform_add_service.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), mock.patch.object(
            DbtRunner, "run", return_value=None
        ), mock.patch(
            "meltano.cli.elt.install_plugins", return_value=True
        ) as install_plugin_mock:
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            install_plugin_mock.assert_not_called()


class TestCliEltScratchpadFour:
    @pytest.fixture(scope="class")
    def tap_csv(self, project_add_service):
        try:
            return project_add_service.add(PluginType.EXTRACTORS, "tap-csv")
        except PluginAlreadyAddedException as err:
            return err.plugin

    @pytest.mark.backend("sqlite")
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    def test_elt_transform_only_unknown(
        self,
        google_tracker,
        cli_runner,
        project,
        tap_csv,
        target,
        plugin_discovery_service,
    ):
        # exit cleanly when `meltano elt ... --transform only` runs for
        # a tap with no default transforms

        args = ["elt", tap_csv.name, target.name, "--transform", "only"]

        with mock.patch(
            "meltano.cli.elt.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), mock.patch(
            "meltano.core.elt_context.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), mock.patch.object(
            DbtRunner, "run", return_value=None
        ), mock.patch(
            "meltano.cli.elt.install_plugins", return_value=True
        ) as install_plugin_mock:
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            install_plugin_mock.assert_called_once_with(
                project,
                [
                    PluginRef(PluginType.FILES, "dbt"),
                    PluginRef(PluginType.TRANSFORMERS, "dbt"),
                ],
                reason=PluginInstallReason.ADD,
            )
