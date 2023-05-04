from __future__ import annotations

import os
import shutil

import mock
import pytest

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.plugin import PluginType
from meltano.core.project_add_service import PluginAlreadyAddedException


class TestCliInstall:
    @pytest.fixture(scope="class")
    def tap_gitlab(self, project_add_service):
        try:
            return project_add_service.add(PluginType.EXTRACTORS, "tap-gitlab")
        except PluginAlreadyAddedException as err:
            return err.plugin

    @pytest.mark.order(0)
    def test_install(self, project, tap, tap_gitlab, target, dbt, cli_runner):
        with mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True

            result = cli_runner.invoke(cli, ["install"])
            assert_cli_runner(result)

            install_plugin_mock.assert_called_once_with(
                project,
                [tap, tap_gitlab, target, dbt],
                parallelism=None,
                clean=False,
                force=False,
            )

    @pytest.mark.usefixtures("dbt")
    def test_install_type(
        self,
        project,
        tap,
        tap_gitlab,
        target,
        mapper,
        cli_runner,
    ):
        with mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock_e:
            install_plugin_mock_e.return_value = True

            result = cli_runner.invoke(cli, ["install", "extractors"])
            assert_cli_runner(result)

            install_plugin_mock_e.assert_called_once_with(
                project,
                [tap, tap_gitlab],
                parallelism=None,
                clean=False,
                force=False,
            )

        with mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock_l:
            install_plugin_mock_l.return_value = True

            result = cli_runner.invoke(cli, ["install", "loaders"])
            assert_cli_runner(result)

            install_plugin_mock_l.assert_called_once_with(
                project,
                [target],
                parallelism=None,
                clean=False,
                force=False,
            )

        with mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock_m:
            install_plugin_mock_m.return_value = True

            result = cli_runner.invoke(cli, ["install", "mappers"])
            assert_cli_runner(result)

            assert install_plugin_mock_m.call_count == 1
            seen_plugins = install_plugin_mock_m.call_args[0][1]
            assert len(seen_plugins) == 3
            assert mapper in seen_plugins
            mappings_seen = 0
            for found in seen_plugins:
                assert found == mapper
                if found.extra_config.get("_mapping"):
                    mappings_seen += 1
            assert mappings_seen == 2

    @pytest.mark.usefixtures("tap_gitlab", "dbt")
    def test_install_type_name(
        self,
        project,
        tap,
        target,
        mapper,
        cli_runner,
    ):
        with mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock_e:
            install_plugin_mock_e.return_value = True

            result = cli_runner.invoke(cli, ["install", "extractor", tap.name])
            assert_cli_runner(result)

            install_plugin_mock_e.assert_called_once_with(
                project,
                [tap],
                parallelism=None,
                clean=False,
                force=False,
            )

        with mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock_l:
            install_plugin_mock_l.return_value = True

            result = cli_runner.invoke(cli, ["install", "loader", target.name])
            assert_cli_runner(result)

            install_plugin_mock_l.assert_called_once_with(
                project,
                [target],
                parallelism=None,
                clean=False,
                force=False,
            )

        with mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock_m:
            install_plugin_mock_m.return_value = True

            result = cli_runner.invoke(cli, ["install", "mapper", mapper.name])
            assert_cli_runner(result)

            assert install_plugin_mock_m.call_count == 1
            seen_plugins = install_plugin_mock_m.call_args[0][1]
            assert len(seen_plugins) == 3
            assert mapper in seen_plugins
            mappings_seen = 0
            for found in seen_plugins:
                assert found == mapper
                if found.extra_config.get("_mapping"):
                    mappings_seen += 1
            assert mappings_seen == 2

    @pytest.mark.usefixtures("target", "dbt")
    def test_install_multiple(self, project, tap, tap_gitlab, cli_runner):
        with mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True

            result = cli_runner.invoke(
                cli,
                ["install", "extractors", tap.name, tap_gitlab.name],
            )
            assert_cli_runner(result)

            install_plugin_mock.assert_called_once_with(
                project,
                [tap, tap_gitlab],
                parallelism=None,
                clean=False,
                force=False,
            )

    def test_install_parallel(
        self,
        project,
        tap,
        tap_gitlab,
        target,
        dbt,
        mapper,
        cli_runner,
    ):
        with mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True

            result = cli_runner.invoke(cli, ["install", "--parallelism=10"])
            assert_cli_runner(result)

            assert install_plugin_mock.call_count == 1

            commands = [
                args
                for _, args, kwargs in install_plugin_mock.mock_calls
                if args and isinstance(args, tuple)
            ]
            kwargs = install_plugin_mock.mock_calls[0][2]
            assert len(commands) == 1

            assert commands[0][0] == project
            for cli_arg in (dbt, tap_gitlab, target, tap, mapper):
                assert cli_arg in commands[0][1]

            assert kwargs["parallelism"] == 10
            assert not kwargs["clean"]

            mappers = [m for m in commands[0][1] if m == mapper]
            assert len(mappers) == 3

    def test_clean_install(
        self,
        project,
        tap,
        tap_gitlab,
        target,
        dbt,
        mapper,
        cli_runner,
    ):
        with mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True

            result = cli_runner.invoke(cli, ["install", "--clean"])
            assert_cli_runner(result)

            assert install_plugin_mock.call_count == 1

            commands = [
                args
                for _, args, kwargs in install_plugin_mock.mock_calls
                if args and isinstance(args, tuple)
            ]
            kwargs = install_plugin_mock.mock_calls[0][2]
            assert len(commands) == 1

            assert commands[0][0] == project
            for cli_arg in (dbt, tap_gitlab, target, tap, mapper):
                assert cli_arg in commands[0][1]

            assert not kwargs["parallelism"]
            assert kwargs["clean"]

            mappers = [m for m in commands[0][1] if m == mapper]
            assert len(mappers) == 3

    @pytest.mark.usefixtures("tap_gitlab", "target")
    def test_install_schedule(
        self,
        project,
        tap_gitlab,
        target,
        dbt,
        mapper,
        cli_runner,
        schedule_service,
        job_schedule,
        task_sets_service,
    ):
        with mock.patch(
            "meltano.cli.install.ScheduleService",
            return_value=schedule_service,
        ), mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True
            schedule_service.task_sets_service = task_sets_service
            from meltano.core.task_sets import TaskSets

            mapping = mapper.extra_config.get("_mappings")[0].get("name")
            task_sets_service.add(
                TaskSets(
                    job_schedule.job,
                    [tap_gitlab.name, mapping, target.name, dbt.name],
                ),
            )
            result = cli_runner.invoke(
                cli,
                ["install", "--schedule", job_schedule.name],
            )
            assert_cli_runner(result)

            install_plugin_mock.assert_called_once()
            assert install_plugin_mock.mock_calls[0].args[0] == project

            plugins_installed = [
                plugin.name for plugin in install_plugin_mock.mock_calls[0].args[1]
            ]
            plugins_expected = [tap_gitlab.name, mapper.name, target.name, dbt.name]
            assert sorted(plugins_installed) == sorted(plugins_expected)
            assert install_plugin_mock.mock_calls[0].kwargs["parallelism"] is None
            assert install_plugin_mock.mock_calls[0].kwargs["clean"] is False
            assert install_plugin_mock.mock_calls[0].kwargs["force"] is False

    def test_install_schedule_elt(
        self,
        project,
        tap,
        target,
        cli_runner,
        schedule_service,
        elt_schedule,
        task_sets_service,
    ):
        with mock.patch(
            "meltano.cli.install.ScheduleService",
            return_value=schedule_service,
        ), mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True
            schedule_service.task_sets_service = task_sets_service

            result = cli_runner.invoke(
                cli,
                ["install", "--schedule", elt_schedule.name],
            )
            assert_cli_runner(result)

            install_plugin_mock.assert_called_once()
            assert install_plugin_mock.mock_calls[0].args[0] == project

            plugins_installed = [
                plugin.name for plugin in install_plugin_mock.mock_calls[0].args[1]
            ]
            plugins_expected = [
                tap.name,
                target.name,
            ]
            assert sorted(plugins_installed) == sorted(plugins_expected)
            assert install_plugin_mock.mock_calls[0].kwargs["parallelism"] is None
            assert install_plugin_mock.mock_calls[0].kwargs["clean"] is False
            assert install_plugin_mock.mock_calls[0].kwargs["force"] is False


# un_engine_uri forces us to create a new project, we must do this before the
# project fixture creates the project see
# https://github.com/meltano/meltano/pull/6407#issuecomment-1200516464
# For more details
@pytest.mark.order(-1)
@pytest.mark.usefixtures("un_engine_uri", "project_function")
def test_new_folder_should_autocreate_on_install(cli_runner):
    """Be sure .meltano auto creates a db on install by default.

    We had a case https://github.com/meltano/meltano/issues/6383
    that caused the meltano db to not be recreated.
    """
    shutil.rmtree(".meltano")
    result = cli_runner.invoke(cli, ["install"])
    assert result
    assert os.path.exists(".meltano/meltano.db")
