import asyncio
import json

import pytest
from asserts import assert_cli_runner
from asynctest import CoroutineMock, mock
from meltano.cli import cli
from meltano.core.job import Job, State
from meltano.core.logging.utils import remove_ansi_escape_sequences
from meltano.core.plugin import PluginRef, PluginType
from meltano.core.plugin.dbt import DbtPlugin
from meltano.core.plugin.singer import SingerTap
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.project_add_service import PluginAlreadyAddedException
from meltano.core.runner.dbt import DbtRunner
from meltano.core.runner.singer import SingerRunner
from meltano.core.tracking import GoogleAnalyticsTracker


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
        process_mock.stdin.wait_closed = CoroutineMock(return_value=True)
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

    # Have `target.wait` take 1s to make sure the tap always finishes before the target
    async def wait_mock():
        await asyncio.sleep(1)
        return target.wait.return_value

    target.wait.side_effect = wait_mock

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
    def test_elt(
        self,
        google_tracker,
        cli_runner,
        project,
        tap,
        target,
        tap_process,
        target_process,
        project_plugins_service,
        job_logging_service,
    ):
        result = cli_runner.invoke(cli, ["elt"])
        assert result.exit_code == 2

        job_id = "pytest_test_elt"
        args = ["elt", "--job_id", job_id, tap.name, target.name]

        # exit cleanly when everything is fine
        create_subprocess_exec = CoroutineMock(
            side_effect=(tap_process, target_process)
        )
        with mock.patch.object(SingerTap, "discover_catalog"), mock.patch.object(
            SingerTap, "apply_catalog_rules"
        ), mock.patch(
            "meltano.core.plugin_invoker.asyncio"
        ) as asyncio_mock, mock.patch(
            "meltano.cli.elt.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec

            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            assert_lines(
                result.stdout,
                "meltano     | elt       | Running extract & load...\n",
                "meltano     | elt       | No state was found, complete import.\n",
                "meltano     | elt       | Incremental state has been updated at",  # followed by timestamp
                "meltano     | elt       | Extract & load complete!\n",
                "meltano     | elt       | Transformation skipped.\n",
            )

            assert_lines(
                result.stderr,
                "tap-mock    | extractor | Starting\n",
                "tap-mock    | extractor | Running\n",
                "tap-mock    | extractor | Done\n",
                "target-mock | loader    | Starting\n",
                "target-mock | loader    | Running\n",
                "target-mock | loader    | Done\n",
            )

        job_logging_service.delete_all_logs(job_id)

        exc = Exception("This is a grave danger.")
        with mock.patch.object(SingerRunner, "run", side_effect=exc), mock.patch(
            "meltano.cli.elt.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert result.exception == exc

            lines = [
                "meltano     | elt       | Running extract & load...\n",
                "meltano     | elt       | This is a grave danger.\n",
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
        project_plugins_service,
        job_logging_service,
        monkeypatch,
    ):
        job_id = "pytest_test_elt_debug"
        args = ["elt", "--job_id", job_id, tap.name, target.name]

        job_logging_service.delete_all_logs(job_id)

        create_subprocess_exec = CoroutineMock(
            side_effect=(tap_process, target_process)
        )
        with mock.patch.object(SingerTap, "discover_catalog"), mock.patch.object(
            SingerTap, "apply_catalog_rules"
        ), mock.patch(
            "meltano.core.plugin_invoker.asyncio"
        ) as asyncio_mock, mock.patch(
            "meltano.cli.elt.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            asyncio_mock.create_subprocess_exec = create_subprocess_exec

            monkeypatch.setenv("MELTANO_CLI_LOG_LEVEL", "debug")
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            stdout_lines = [
                "meltano           | elt       | INFO Running extract & load...\n",
                "meltano           | elt       | DEBUG Created configuration at",  # followed by path
                "meltano           | elt       | DEBUG Could not find tap.properties.json in",  # followed by path
                "meltano           | elt       | DEBUG Could not find state.json in",  # followed by path
                "meltano           | elt       | DEBUG Created configuration at",  # followed by path
                "meltano           | elt       | WARNING No state was found, complete import.\n",
                "meltano           | elt       | INFO Incremental state has been updated at",  # followed by timestamp
                "meltano           | elt       | DEBUG Incremental state: {'line': 1}\n",
                "meltano           | elt       | DEBUG Incremental state: {'line': 2}\n",
                "meltano           | elt       | DEBUG Incremental state: {'line': 3}\n",
                "meltano           | elt       | INFO Extract & load complete!\n",
                "meltano           | elt       | INFO Transformation skipped.\n",
            ]

            stderr_lines = [
                "tap-mock          | extractor | Starting\n",
                "tap-mock          | extractor | Running\n",
                "tap-mock (out)    | extractor | SCHEMA\n",
                "tap-mock (out)    | extractor | RECORD\n",
                "tap-mock (out)    | extractor | STATE\n",
                "tap-mock          | extractor | Done\n",
                "target-mock       | loader    | Starting\n",
                "target-mock       | loader    | Running\n",
                'target-mock (out) | loader    | {"line": 1}\n',
                'target-mock (out) | loader    | {"line": 2}\n',
                'target-mock (out) | loader    | {"line": 3}\n',
                "target-mock       | loader    | Done\n",
            ]

            assert_lines(result.stdout, *stdout_lines)
            assert_lines(result.stderr, *stderr_lines)

            log = job_logging_service.get_latest_log(job_id)
            assert_lines(
                log,
                *(
                    remove_ansi_escape_sequences(line)
                    for line in stdout_lines + stderr_lines
                ),
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
        project_plugins_service,
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
            "meltano.cli.elt.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert "Extractor failed" in str(result.exception)

            assert_lines(
                result.stdout,
                "meltano     | elt       | Running extract & load...\n",
                "meltano     | elt       | Extraction failed (1): Failure\n",
            )
            assert_lines(
                result.stderr,
                "tap-mock    | extractor | Starting\n",
                "tap-mock    | extractor | Running\n",
                "tap-mock    | extractor | Failure\n",
                "target-mock | loader    | Starting\n",
                "target-mock | loader    | Running\n",
                "target-mock | loader    | Done\n",
            )

    @pytest.mark.backend("sqlite")
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    def test_elt_target_failure_before_tap_finishes(
        self,
        google_tracker,
        cli_runner,
        project,
        tap,
        target,
        tap_process,
        target_process,
        project_plugins_service,
    ):
        job_id = "pytest_test_elt"
        args = ["elt", "--job_id", job_id, tap.name, target.name]

        # Have `tap_process.wait` take 2s to make sure the target can fail before tap finishes
        async def tap_wait_mock():
            await asyncio.sleep(2)
            return tap_process.wait.return_value

        tap_process.wait.side_effect = tap_wait_mock

        # Writing to target stdin will fail because (we'll pretend) it has already died
        target_process.stdin = mock.Mock(spec=asyncio.StreamWriter)
        target_process.stdin.write.side_effect = BrokenPipeError
        target_process.stdin.drain = CoroutineMock(side_effect=ConnectionResetError)
        target_process.stdin.wait_closed = CoroutineMock(return_value=True)

        # Have `target_process.wait` take 1s to make sure the `stdin.write`/`drain` exceptions can be raised
        async def target_wait_mock():
            await asyncio.sleep(1)
            return 1

        target_process.wait.side_effect = target_wait_mock

        target_process.stderr.readline.side_effect = (
            b"Starting\n",
            b"Running\n",
            b"Failure\n",
        )

        invoke_async = CoroutineMock(side_effect=(tap_process, target_process))
        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ) as invoke_async, mock.patch(
            "meltano.cli.elt.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert "Loader failed" in str(result.exception)

            assert_lines(
                result.stdout,
                "meltano     | elt       | Running extract & load...\n",
                "meltano     | elt       | Loading failed (1): Failure\n",
            )
            assert_lines(
                result.stderr,
                "tap-mock    | extractor | Starting\n",
                "tap-mock    | extractor | Running\n",
                "tap-mock    | extractor | Done\n",
                "target-mock | loader    | Starting\n",
                "target-mock | loader    | Running\n",
                "target-mock | loader    | Failure\n",
            )

    @pytest.mark.backend("sqlite")
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    def test_elt_target_failure_after_tap_finishes(
        self,
        google_tracker,
        cli_runner,
        project,
        tap,
        target,
        tap_process,
        target_process,
        project_plugins_service,
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
            "meltano.cli.elt.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert "Loader failed" in str(result.exception)

            assert_lines(
                result.stdout,
                "meltano     | elt       | Running extract & load...\n",
                "meltano     | elt       | Loading failed (1): Failure\n",
            )
            assert_lines(
                result.stderr,
                "tap-mock    | extractor | Starting\n",
                "tap-mock    | extractor | Running\n",
                "tap-mock    | extractor | Done\n",
                "target-mock | loader    | Starting\n",
                "target-mock | loader    | Running\n",
                "target-mock | loader    | Failure\n",
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
        project_plugins_service,
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
            "meltano.cli.elt.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert "Extractor and loader failed" in str(result.exception)

            assert_lines(
                result.stdout,
                "meltano     | elt       | Running extract & load...\n",
                "meltano     | elt       | Extraction failed (1): Failure\n",
                "meltano     | elt       | Loading failed (1): Failure\n",
            )
            assert_lines(
                result.stderr,
                "tap-mock    | extractor | Starting\n",
                "tap-mock    | extractor | Running\n",
                "tap-mock    | extractor | Failure\n",
                "target-mock | loader    | Starting\n",
                "target-mock | loader    | Running\n",
                "target-mock | loader    | Failure\n",
            )

    @pytest.mark.backend("sqlite")
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    def test_elt_tap_line_length_limit_error(
        self,
        google_tracker,
        cli_runner,
        project,
        tap,
        target,
        tap_process,
        target_process,
        project_plugins_service,
    ):
        job_id = "pytest_test_elt"
        args = ["elt", "--job_id", job_id, tap.name, target.name]

        # Raise a ValueError wrapping a LimitOverrunError, like StreamReader.readline does:
        # https://github.com/python/cpython/blob/v3.8.7/Lib/asyncio/streams.py#L549
        try:  # noqa: WPS328
            raise asyncio.LimitOverrunError(
                "Separator is not found, and chunk exceed the limit", 0
            )
        except asyncio.LimitOverrunError as err:
            try:  # noqa: WPS328, WPS505
                # `ValueError` needs to be raised from inside the except block
                # for `LimitOverrunError` so that `__context__` is set.
                raise ValueError(str(err))
            except ValueError as wrapper_err:
                tap_process.stdout.readline.side_effect = wrapper_err

        # Have `tap_process.wait` take 1s to make sure the LimitOverrunError exception can be raised before tap finishes
        async def wait_mock():
            await asyncio.sleep(1)
            return tap_process.wait.return_value

        tap_process.wait.side_effect = wait_mock

        invoke_async = CoroutineMock(side_effect=(tap_process, target_process))
        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ) as invoke_async, mock.patch(
            "meltano.cli.elt.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert "Output line length limit exceeded" in str(result.exception)

            assert_lines(
                result.stdout,
                "meltano     | elt       | Running extract & load...\n",
                "meltano     | elt       | The extractor generated a message exceeding the message size limit of 5.0MiB (half the buffer size of 10.0MiB).\n",
            )

            assert_lines(
                result.stderr,
                "meltano     | elt       | ELT could not be completed: Output line length limit exceeded\n",
            )

    @pytest.mark.backend("sqlite")
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    def test_elt_output_handler_error(
        self,
        google_tracker,
        cli_runner,
        project,
        tap,
        target,
        tap_process,
        target_process,
        project_plugins_service,
    ):
        job_id = "pytest_test_elt"
        args = ["elt", "--job_id", job_id, tap.name, target.name]

        exc = Exception("Failed to read from target stderr.")
        target_process.stderr.readline.side_effect = exc

        # Have `tap_process.wait` take 1s to make sure the exception can be raised before tap finishes
        async def wait_mock():
            await asyncio.sleep(1)
            return tap_process.wait.return_value

        tap_process.wait.side_effect = wait_mock

        invoke_async = CoroutineMock(side_effect=(tap_process, target_process))
        with mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ) as invoke_async, mock.patch(
            "meltano.cli.elt.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert result.exception == exc

            assert_lines(
                result.stdout,
                "meltano     | elt       | Running extract & load...\n",
                "meltano     | elt       | Failed to read from target stderr.\n",
            )

    def test_elt_already_running(
        self, cli_runner, tap, target, project_plugins_service, session
    ):
        job_id = "already_running"
        args = ["elt", "--job_id", job_id, tap.name, target.name]

        existing_job = Job(job_id=job_id, state=State.RUNNING)
        existing_job.save(session)

        with mock.patch(
            "meltano.cli.elt.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch(
            "meltano.cli.elt.project_engine", return_value=(None, lambda: session)
        ):
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert f"Another '{job_id}' pipeline is already running" in str(
                result.exception
            )

    def test_dump_catalog(
        self,
        cli_runner,
        project,
        tap,
        target,
        project_plugins_service,
        plugin_settings_service_factory,
    ):
        catalog = {"streams": []}
        with project.root.joinpath("catalog.json").open("w") as catalog_file:
            json.dump(catalog, catalog_file)

        job_id = "pytest_test_elt"
        args = [
            "elt",
            "--job_id",
            job_id,
            tap.name,
            target.name,
            "--catalog",
            "catalog.json",
            "--dump",
            "catalog",
        ]

        with mock.patch(
            "meltano.cli.elt.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            assert json.loads(result.stdout) == catalog

    def test_dump_state(
        self,
        session,
        cli_runner,
        project,
        tap,
        target,
        project_plugins_service,
        plugin_settings_service_factory,
    ):
        state = {"success": True}
        with project.root.joinpath("state.json").open("w") as state_file:
            json.dump(state, state_file)

        job_id = "pytest_test_elt"
        args = [
            "elt",
            "--job_id",
            job_id,
            tap.name,
            target.name,
            "--state",
            "state.json",
            "--dump",
            "state",
        ]

        with mock.patch(
            "meltano.cli.elt.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch.object(SingerTap, "discover_catalog"), mock.patch.object(
            SingerTap, "apply_catalog_rules"
        ):
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            assert json.loads(result.stdout) == state

    def test_dump_extractor_config(
        self,
        cli_runner,
        project,
        tap,
        target,
        project_plugins_service,
        plugin_settings_service_factory,
    ):
        job_id = "pytest_test_elt"
        args = [
            "elt",
            "--job_id",
            job_id,
            tap.name,
            target.name,
            "--dump",
            "extractor-config",
        ]

        settings_service = plugin_settings_service_factory(tap)

        with mock.patch(
            "meltano.cli.elt.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch.object(SingerTap, "discover_catalog"), mock.patch.object(
            SingerTap, "apply_catalog_rules"
        ):
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            assert json.loads(result.stdout) == settings_service.as_dict(
                extras=False, process=True
            )

    def test_dump_loader_config(
        self,
        cli_runner,
        project,
        tap,
        target,
        project_plugins_service,
        plugin_settings_service_factory,
    ):
        job_id = "pytest_test_elt"
        args = [
            "elt",
            "--job_id",
            job_id,
            tap.name,
            target.name,
            "--dump",
            "loader-config",
        ]

        settings_service = plugin_settings_service_factory(target)

        with mock.patch(
            "meltano.cli.elt.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch.object(SingerTap, "discover_catalog"), mock.patch.object(
            SingerTap, "apply_catalog_rules"
        ):
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            assert json.loads(result.stdout) == settings_service.as_dict(
                extras=False, process=True
            )


class TestCliEltScratchpadTwo:
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
        project_plugins_service,
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
            "meltano.cli.elt.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch(
            "meltano.core.transform_add_service.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            assert_lines(
                result.stdout,
                "meltano     | elt       | Running extract & load...\n",
                "meltano     | elt       | Extract & load complete!\n",
                "meltano     | elt       | Running transformation...\n",
                "meltano     | elt       | Transformation complete!\n",
            )

            assert_lines(
                result.stderr,
                "tap-mock    | extractor | Starting\n",
                "tap-mock    | extractor | Running\n",
                "tap-mock    | extractor | Done\n",
                "target-mock | loader    | Starting\n",
                "target-mock | loader    | Running\n",
                "target-mock | loader    | Done\n",
                "dbt         | main      | Starting\n",
                "dbt         | main      | Running\n",
                "dbt         | main      | Done\n",
            )

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
        project_plugins_service,
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
            "meltano.cli.elt.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch(
            "meltano.core.transform_add_service.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, args)
            assert result.exit_code == 1
            assert "`dbt run` failed" in str(result.exception)

            assert_lines(
                result.stdout,
                "meltano     | elt       | Running extract & load...\n",
                "meltano     | elt       | Extract & load complete!\n",
                "meltano     | elt       | Running transformation...\n",
                "meltano     | elt       | Transformation failed (1): Failure\n",
            )

            assert_lines(
                result.stderr,
                "tap-mock    | extractor | Starting\n",
                "tap-mock    | extractor | Running\n",
                "tap-mock    | extractor | Done\n",
                "target-mock | loader    | Starting\n",
                "target-mock | loader    | Running\n",
                "target-mock | loader    | Done\n",
                "dbt         | main      | Starting\n",
                "dbt         | main      | Running\n",
                "dbt         | main      | Failure\n",
            )


class TestCliEltScratchpadThree:
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
        project_plugins_service,
    ):
        args = ["elt", tap.name, target.name, "--transform", "only"]

        with mock.patch(
            "meltano.cli.elt.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch(
            "meltano.core.transform_add_service.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch.object(
            DbtRunner, "run", new=CoroutineMock()
        ):
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            assert_lines(
                result.output,
                "meltano | elt    | Extract & load skipped.\n",
                "meltano | elt    | Running transformation...\n",
                "meltano | elt    | Transformation complete!\n",
            )

    @pytest.mark.backend("sqlite")
    @mock.patch.object(GoogleAnalyticsTracker, "track_data", return_value=None)
    def test_elt_transform_only_with_transform(
        self,
        google_tracker,
        cli_runner,
        project,
        tap,
        target,
        dbt,
        tap_mock_transform,
        project_plugins_service,
    ):
        args = ["elt", tap.name, target.name, "--transform", "only"]

        with mock.patch(
            "meltano.cli.elt.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch(
            "meltano.core.transform_add_service.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch.object(
            DbtRunner, "run", new=CoroutineMock()
        ):
            result = cli_runner.invoke(cli, args)
            assert_cli_runner(result)

            assert_lines(
                result.output,
                "meltano | elt    | Extract & load skipped.\n",
                "meltano | elt    | Running transformation...\n",
                "meltano | elt    | Transformation complete!\n",
            )
