import pytest
import os
import logging
from unittest import mock
from asynctest import CoroutineMock
from functools import partial

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.project_add_service import PluginAlreadyAddedException
from meltano.core.plugin import PluginType, PluginRef
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.plugin.dbt import DbtPlugin
from meltano.core.runner.singer import SingerRunner
from meltano.core.runner.dbt import DbtRunner
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.job import Job
from meltano.core.logging.utils import remove_ansi_escape_sequences


def assert_lines(output, *lines):
    for line in lines:
        assert line in output


@pytest.fixture(scope="class")
def tap_mock_transform(project_add_service):
    try:
        return project_add_service.add(PluginType.TRANSFORMS, "tap-mock-transform")
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture()
def process_mock_factory():
    def _factory(name):
        process_mock = mock.Mock()
        process_mock.name = name
        process_mock.wait = CoroutineMock(return_value=0)
        process_mock.returncode = 0
        return process_mock

    return _factory


@pytest.fixture()
def tap_process(process_mock_factory, tap):
    tap = process_mock_factory(tap)
    tap.stdout.at_eof.side_effect = (False, False, False, True)
    tap.stdout.readline = CoroutineMock(
        side_effect=(b"SCHEMA\n", b"RECORD\n", b"STATE\n")
    )
    tap.stderr.at_eof.side_effect = (False, False, False, True)
    tap.stderr.readline = CoroutineMock(
        side_effect=(b"Starting\n", b"Running\n", b"Done\n")
    )
    return tap


@pytest.fixture()
def target_process(process_mock_factory, target):
    target = process_mock_factory(target)
    target.stdout.at_eof.side_effect = (False, False, False, True)
    target.stdout.readline = CoroutineMock(
        side_effect=(b'{"line": 1}\n', b'{"line": 2}\n', b'{"line": 3}\n')
    )
    target.stderr.at_eof.side_effect = (False, False, False, True)
    target.stderr.readline = CoroutineMock(
        side_effect=(b"Starting\n", b"Running\n", b"Done\n")
    )
    return target


@pytest.fixture()
def silent_dbt_process(process_mock_factory, dbt):
    dbt = process_mock_factory(dbt)
    dbt.stdout.at_eof.side_effect = (True, True)
    dbt.stderr.at_eof.side_effect = (True, True)
    return dbt


@pytest.fixture()
def dbt_process(process_mock_factory, dbt):
    dbt = process_mock_factory(dbt)
    dbt.stdout.at_eof.side_effect = (True,)
    dbt.stderr.at_eof.side_effect = (False, False, False, True)
    dbt.stderr.readline = CoroutineMock(
        side_effect=(b"Starting\n", b"Running\n", b"Done\n")
    )
    return dbt


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
            SingerRunner, "run", new=CoroutineMock()
        ), mock.patch(
            "meltano.cli.elt.install_plugins", return_value=True
        ) as install_plugin_mock:
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            assert_lines(
                result.output,
                "meltano | Extractor 'tap-mock' is missing, adding it to your project...\n",
                "meltano | Loader 'target-mock' is missing, adding it to your project...\n",
                "meltano     | Added extractor 'tap-mock' to your Meltano project\n",
                "meltano     | Added loader 'target-mock' to your Meltano project\n",
                "meltano     | Running extract & load...\n",
                "meltano     | Extract & load complete!\n",
                "meltano     | Transformation skipped.\n",
            )

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
        tap_process,
        target_process,
        plugin_discovery_service,
        job_logging_service,
    ):
        result = cli_runner.invoke(cli, ["elt"])
        assert result.exit_code == 2

        job_id = "pytest_test_elt"
        args = ["elt", "--job_id", job_id, tap.name, target.name]

        # exit cleanly when everything is fine
        invoke_async = CoroutineMock(side_effect=(tap_process, target_process))
        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ) as invoke_async, mock.patch(
            "meltano.cli.elt.install_plugins", return_value=True
        ) as install_plugin_mock, mock.patch(
            "meltano.core.elt_context.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ):
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            assert_lines(
                result.stdout,
                "meltano     | Running extract & load...\n",
                "meltano     | No state was found, complete import.\n",
                "meltano     | Incremental state has been updated at",  # followed by timestamp
                "meltano     | Extract & load complete!\n",
                "meltano     | Transformation skipped.\n",
            )

            assert_lines(
                result.stderr,
                "tap-mock    | Starting\n",
                "tap-mock    | Running\n",
                "tap-mock    | Done\n",
                "target-mock | Starting\n",
                "target-mock | Running\n",
                "target-mock | Done\n",
            )

            install_plugin_mock.assert_not_called()

        # aborts when there is an exception
        with mock.patch("meltano.cli.elt.install_missing_plugins", return_value=None):
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert str(result.exception) == "Failed to install missing plugins"

        job_logging_service.delete_all_logs(job_id)

        exc = Exception("This is a grave danger.")
        with mock.patch.object(SingerRunner, "run", side_effect=exc), mock.patch(
            "meltano.core.elt_context.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ):
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert result.exception == exc

            lines = [
                "meltano     | Running extract & load...\n",
                "meltano     | This is a grave danger.\n",
                "Traceback",
                "Exception: This is a grave danger.\n",
            ]

            assert_lines(result.output, *lines)

            # ensure there is a log of this exception
            log = job_logging_service.get_latest_log(job_id)
            assert_lines(log, *(remove_ansi_escape_sequences(l) for l in lines))

    @pytest.mark.backend("sqlite")
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    def test_elt_debug_logging(
        self,
        google_tracker,
        cli_runner,
        project,
        tap,
        target,
        tap_process,
        target_process,
        plugin_discovery_service,
        job_logging_service,
        monkeypatch,
    ):
        job_id = "pytest_test_elt_debug"
        args = ["elt", "--job_id", job_id, tap.name, target.name]

        job_logging_service.delete_all_logs(job_id)

        invoke_async = CoroutineMock(side_effect=(tap_process, target_process))
        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ) as invoke_async, mock.patch(
            "meltano.cli.elt.install_plugins", return_value=True
        ) as install_plugin_mock, mock.patch(
            "meltano.core.elt_context.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ):
            monkeypatch.setenv("MELTANO_CLI_LOG_LEVEL", "debug")
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            stdout_lines = [
                "meltano           | INFO Running extract & load...\n",
                "meltano           | DEBUG Created configuration at",  # followed by path
                "meltano           | DEBUG Could not find tap.properties.json in",  # followed by path
                "meltano           | DEBUG Could not find state.json in",  # followed by path
                "meltano           | DEBUG Created configuration at",  # followed by path
                "meltano           | WARNING No state was found, complete import.\n",
                "meltano           | INFO Incremental state has been updated at",  # followed by timestamp
                "meltano           | DEBUG Incremental state: {'line': 1}\n",
                "meltano           | DEBUG Incremental state: {'line': 2}\n",
                "meltano           | DEBUG Incremental state: {'line': 3}\n",
                "meltano           | INFO Extract & load complete!\n",
                "meltano           | INFO Transformation skipped.\n",
            ]

            stderr_lines = [
                "tap-mock          | Starting\n",
                "tap-mock          | Running\n",
                "tap-mock (out)    | SCHEMA\n",
                "tap-mock (out)    | RECORD\n",
                "tap-mock (out)    | STATE\n",
                "tap-mock          | Done\n",
                "target-mock       | Starting\n",
                "target-mock       | Running\n",
                'target-mock (out) | {"line": 1}\n',
                'target-mock (out) | {"line": 2}\n',
                'target-mock (out) | {"line": 3}\n',
                "target-mock       | Done\n",
            ]

            assert_lines(result.stdout, *stdout_lines)
            assert_lines(result.stderr, *stderr_lines)

            log = job_logging_service.get_latest_log(job_id)
            assert_lines(
                log,
                *(remove_ansi_escape_sequences(l) for l in stdout_lines + stderr_lines)
            )

    @pytest.mark.backend("sqlite")
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    def test_elt_tap_failure(
        self,
        google_tracker,
        cli_runner,
        project,
        tap,
        target,
        tap_process,
        target_process,
        plugin_discovery_service,
    ):
        job_id = "pytest_test_elt"
        args = ["elt", "--job_id", job_id, tap.name, target.name]

        tap_process.wait.return_value = 1
        tap_process.stderr.readline.side_effect = (
            b"Starting\n",
            b"Running\n",
            b"Failure\n",
        )

        invoke_async = CoroutineMock(side_effect=(tap_process, target_process))
        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ) as invoke_async, mock.patch(
            "meltano.cli.elt.install_plugins", return_value=True
        ) as install_plugin_mock, mock.patch(
            "meltano.core.elt_context.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ):
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert "Tap failed" in str(result.exception)

            assert_lines(
                result.stdout,
                "meltano     | Running extract & load...\n",
                "meltano     | Extraction failed (1): Failure\n",
            )
            assert_lines(
                result.stderr,
                "tap-mock    | Starting\n",
                "tap-mock    | Running\n",
                "tap-mock    | Failure\n",
                "target-mock | Starting\n",
                "target-mock | Running\n",
                "target-mock | Done\n",
            )

    @pytest.mark.backend("sqlite")
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    def test_elt_target_failure(
        self,
        google_tracker,
        cli_runner,
        project,
        tap,
        target,
        tap_process,
        target_process,
        plugin_discovery_service,
    ):
        job_id = "pytest_test_elt"
        args = ["elt", "--job_id", job_id, tap.name, target.name]

        target_process.wait.return_value = 1
        target_process.stderr.readline.side_effect = (
            b"Starting\n",
            b"Running\n",
            b"Failure\n",
        )

        invoke_async = CoroutineMock(side_effect=(tap_process, target_process))
        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ) as invoke_async, mock.patch(
            "meltano.cli.elt.install_plugins", return_value=True
        ) as install_plugin_mock, mock.patch(
            "meltano.core.elt_context.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ):
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert "Target failed" in str(result.exception)

            assert_lines(
                result.stdout,
                "meltano     | Running extract & load...\n",
                "meltano     | Loading failed (1): Failure\n",
            )
            assert_lines(
                result.stderr,
                "tap-mock    | Starting\n",
                "tap-mock    | Running\n",
                "tap-mock    | Done\n",
                "target-mock | Starting\n",
                "target-mock | Running\n",
                "target-mock | Failure\n",
            )

    @pytest.mark.backend("sqlite")
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    def test_elt_tap_and_target_failure(
        self,
        google_tracker,
        cli_runner,
        project,
        tap,
        target,
        tap_process,
        target_process,
        plugin_discovery_service,
    ):
        job_id = "pytest_test_elt"
        args = ["elt", "--job_id", job_id, tap.name, target.name]

        tap_process.wait.return_value = 1
        tap_process.stderr.readline.side_effect = (
            b"Starting\n",
            b"Running\n",
            b"Failure\n",
        )

        target_process.wait.return_value = 1
        target_process.stderr.readline.side_effect = (
            b"Starting\n",
            b"Running\n",
            b"Failure\n",
        )

        invoke_async = CoroutineMock(side_effect=(tap_process, target_process))
        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ) as invoke_async, mock.patch(
            "meltano.cli.elt.install_plugins", return_value=True
        ) as install_plugin_mock, mock.patch(
            "meltano.core.elt_context.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ):
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert "Tap and target failed" in str(result.exception)

            assert_lines(
                result.stdout,
                "meltano     | Running extract & load...\n",
                "meltano     | Extraction failed (1): Failure\n",
                "meltano     | Loading failed (1): Failure\n",
            )
            assert_lines(
                result.stderr,
                "tap-mock    | Starting\n",
                "tap-mock    | Running\n",
                "tap-mock    | Failure\n",
                "target-mock | Starting\n",
                "target-mock | Running\n",
                "target-mock | Failure\n",
            )


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
            SingerRunner, "run", new=CoroutineMock()
        ), mock.patch.object(
            DbtRunner, "run", new=CoroutineMock()
        ), mock.patch(
            "meltano.cli.elt.install_plugins", return_value=True
        ) as install_plugin_mock:
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            assert_lines(
                result.output,
                "meltano | Extractor 'tap-mock' is missing, adding it to your project...\n",
                "meltano | Loader 'target-mock' is missing, adding it to your project...\n",
                "meltano | Transform 'tap-mock-transform' is missing, adding it to your project...\n",
                "meltano     | Added extractor 'tap-mock' to your Meltano project\n",
                "meltano     | Added loader 'target-mock' to your Meltano project\n",
                "meltano     | Added transform 'tap-mock-transform' to your Meltano project\n",
                "meltano     | Added related transformer 'dbt' to your Meltano project\n",
                "meltano     | Added related file bundle 'dbt' to your Meltano project\n",
                "meltano     | Running extract & load...\n",
                "meltano     | Extract & load complete!\n",
                "meltano     | Running transformation...\n",
                "meltano     | Transformation complete!\n",
            )

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
        tap_process,
        target_process,
        silent_dbt_process,
        dbt_process,
        tap_mock_transform,
        plugin_discovery_service,
    ):
        args = ["elt", tap.name, target.name, "--transform", "run"]

        invoke_async = CoroutineMock(
            side_effect=(
                tap_process,
                target_process,
                silent_dbt_process,  # dbt clean
                silent_dbt_process,  # dbt deps
                dbt_process,  # dbt run
            )
        )
        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ) as invoke_async, mock.patch(
            "meltano.cli.elt.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), mock.patch(
            "meltano.core.elt_context.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), mock.patch(
            "meltano.core.transform_add_service.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), mock.patch(
            "meltano.cli.elt.install_plugins", return_value=True
        ) as install_plugin_mock:
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            assert_lines(
                result.stdout,
                "meltano     | Running extract & load...\n",
                "meltano     | Extract & load complete!\n",
                "meltano     | Running transformation...\n",
                "meltano     | Transformation complete!\n",
            )

            assert_lines(
                result.stderr,
                "tap-mock    | Starting\n",
                "tap-mock    | Running\n",
                "tap-mock    | Done\n",
                "target-mock | Starting\n",
                "target-mock | Running\n",
                "target-mock | Done\n",
                "dbt         | Starting\n",
                "dbt         | Running\n",
                "dbt         | Done\n",
            )

            install_plugin_mock.assert_not_called()

    @pytest.mark.backend("sqlite")
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    def test_elt_transform_run_dbt_failure(
        self,
        google_tracker,
        cli_runner,
        project,
        tap,
        target,
        dbt,
        tap_process,
        target_process,
        silent_dbt_process,
        dbt_process,
        tap_mock_transform,
        plugin_discovery_service,
    ):
        args = ["elt", tap.name, target.name, "--transform", "run"]

        dbt_process.wait.return_value = 1
        dbt_process.returncode = 1
        dbt_process.stderr.readline.side_effect = (
            b"Starting\n",
            b"Running\n",
            b"Failure\n",
        )

        invoke_async = CoroutineMock(
            side_effect=(
                tap_process,
                target_process,
                silent_dbt_process,  # dbt clean
                silent_dbt_process,  # dbt deps
                dbt_process,  # dbt run
            )
        )
        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ) as invoke_async, mock.patch(
            "meltano.cli.elt.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), mock.patch(
            "meltano.core.elt_context.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), mock.patch(
            "meltano.core.transform_add_service.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), mock.patch(
            "meltano.cli.elt.install_plugins", return_value=True
        ) as install_plugin_mock:
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert "`dbt run` failed" in str(result.exception)

            assert_lines(
                result.stdout,
                "meltano     | Running extract & load...\n",
                "meltano     | Extract & load complete!\n",
                "meltano     | Running transformation...\n",
                "meltano     | Transformation failed (1): Failure\n",
            )

            assert_lines(
                result.stderr,
                "tap-mock    | Starting\n",
                "tap-mock    | Running\n",
                "tap-mock    | Done\n",
                "target-mock | Starting\n",
                "target-mock | Running\n",
                "target-mock | Done\n",
                "dbt         | Starting\n",
                "dbt         | Running\n",
                "dbt         | Failure\n",
            )

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
            DbtRunner, "run", new=CoroutineMock()
        ), mock.patch(
            "meltano.cli.elt.install_plugins", return_value=True
        ) as install_plugin_mock:
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            assert_lines(
                result.output,
                "meltano | Transform 'tap-mock-transform' is missing, adding it to your project...\n",
                "meltano | Added transform 'tap-mock-transform' to your Meltano project\n",
                "meltano | Added related transformer 'dbt' to your Meltano project\n",
                "meltano | Added related file bundle 'dbt' to your Meltano project\n",
                "meltano | Extract & load skipped.\n",
                "meltano | Running transformation...\n",
                "meltano | Transformation complete!\n",
            )

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
            DbtRunner, "run", new=CoroutineMock()
        ), mock.patch(
            "meltano.cli.elt.install_plugins", return_value=True
        ) as install_plugin_mock:
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            assert_lines(
                result.output,
                "meltano | Extract & load skipped.\n",
                "meltano | Running transformation...\n",
                "meltano | Transformation complete!\n",
            )

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
            DbtRunner, "run", new=CoroutineMock()
        ), mock.patch(
            "meltano.cli.elt.install_plugins", return_value=True
        ) as install_plugin_mock:
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            assert_lines(
                result.output,
                "meltano | Transformer 'dbt' is missing, adding it to your project...\n",
                "meltano | Added transformer 'dbt' to your Meltano project\n",
                "meltano | Added related file bundle 'dbt' to your Meltano project\n",
                "meltano | Extract & load skipped.\n",
                "meltano | Running transformation...\n",
                "meltano | Transformation complete!\n",
            )

            install_plugin_mock.assert_called_once_with(
                project,
                [
                    PluginRef(PluginType.FILES, "dbt"),
                    PluginRef(PluginType.TRANSFORMERS, "dbt"),
                ],
                reason=PluginInstallReason.ADD,
            )
