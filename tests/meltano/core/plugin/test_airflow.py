from __future__ import annotations

from configparser import ConfigParser

import pytest
from mock import AsyncMock, mock

from meltano.core.plugin import PluginType
from meltano.core.plugin.airflow import AirflowInvoker
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.plugin_invoker import asyncio

AIRFLOW_CONFIG = """

"""


class TestAirflow:
    @pytest.fixture(scope="class")
    def subject(self, project_add_service):
        with mock.patch.object(PluginInstallService, "install_plugin"):
            return project_add_service.add(PluginType.ORCHESTRATORS, "airflow")

    @pytest.mark.asyncio  # noqa:  WPS210
    async def test_before_configure(  # noqa:  WPS210
        self, subject, project, session, plugin_invoker_factory
    ):
        run_dir = project.run_dir("airflow")

        handle_mock = mock.Mock()
        handle_mock.name = subject.name
        handle_mock.wait = AsyncMock(return_value=0)
        handle_mock.returncode = 0
        handle_mock.communicate = AsyncMock(return_value=(b"2.0.1", None))
        handle_mock.stdout.at_eof.side_effect = (False, True)

        original_exec = asyncio.create_subprocess_exec

        def popen_mock(cmd, *popen_args, **kwargs):
            # first time, it creates the `airflow.cfg`
            if "--help" in popen_args:
                assert "env" in kwargs
                assert kwargs["env"]["AIRFLOW_HOME"] == str(run_dir)

                airflow_cfg = ConfigParser()
                airflow_cfg["core"] = {"dummy": "dummy"}
                airflow_cfg["webserver"] = {"dummy": "dummy"}
                with run_dir.joinpath("airflow.cfg").open("w") as cfg:
                    airflow_cfg.write(cfg)
            # second time, check version
            elif "version" in popen_args:
                return handle_mock
            # third time, it creates the `airflow.db`
            elif {"db", "init"}.issubset(popen_args):
                assert kwargs["env"]["AIRFLOW_HOME"] == str(run_dir)

                project.plugin_dir(subject, "airflow.db").touch()
            else:
                return original_exec(cmd, *popen_args, **kwargs)
            return handle_mock

        with mock.patch.object(
            asyncio, "create_subprocess_exec", side_effect=popen_mock
        ) as popen, mock.patch(
            "meltano.core.plugin_invoker.PluginConfigService.configure"
        ) as configure:
            invoker: AirflowInvoker = plugin_invoker_factory(subject)
            # This ends up calling subject.before_configure
            async with invoker.prepared(session):
                commands = [
                    popen_args
                    for _, popen_args, kwargs in popen.mock_calls
                    if popen_args and isinstance(popen_args, tuple)
                ]
                assert commands[0][1] == "--help"
                assert commands[1][1] == "version"
                assert commands[2][1] == "db"
                assert commands[2][2] == "init"
                assert configure.call_count == 2

                assert run_dir.joinpath("airflow.cfg").exists()
                assert project.plugin_dir(subject, "airflow.db").exists()

                airflow_cfg = ConfigParser()
                with run_dir.joinpath("airflow.cfg").open() as cfg:
                    airflow_cfg.read_file(cfg)

                assert airflow_cfg["core"]["dags_folder"]

            assert not run_dir.joinpath("airflow.cfg").exists()

    @pytest.mark.asyncio
    async def test_before_cleanup(self, subject, plugin_invoker_factory):
        invoker: AirflowInvoker = plugin_invoker_factory(subject)

        assert not invoker.files["config"].exists()

        # No exception should be raised even though the file doesn't exist
        await invoker.cleanup()
