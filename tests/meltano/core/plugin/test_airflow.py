import pytest
from configparser import ConfigParser
from unittest import mock


from meltano.core.plugin import PluginType
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.plugin.airflow import subprocess


AIRFLOW_CONFIG = """

"""


class TestAirflow:
    @pytest.fixture(scope="class")
    def subject(self, project_add_service):
        with mock.patch.object(
            PluginInstallService, "install_plugin"
        ) as install_plugin:
            return project_add_service.add(PluginType.ORCHESTRATORS, "airflow")

    def test_before_configure(self, subject, project, session, plugin_invoker_factory):
        run_dir = project.run_dir("airflow")

        handle_mock = mock.Mock()
        handle_mock.wait.return_value = 0

        original_popen = subprocess.Popen

        def popen_mock(popen_args, *args, **kwargs):
            # first time, it creates the `airflow.cfg`
            if "--help" in popen_args:
                assert kwargs["env"]["AIRFLOW_HOME"] == str(run_dir)

                airflow_cfg = ConfigParser()
                airflow_cfg["core"] = {"dummy": "dummy"}
                airflow_cfg["webserver"] = {"dummy": "dummy"}
                with run_dir.joinpath("airflow.cfg").open("w") as cfg:
                    airflow_cfg.write(cfg)

            # second time, it creates the `airflow.db`
            elif "initdb" in popen_args:
                assert kwargs["env"]["AIRFLOW_HOME"] == str(run_dir)

                project.plugin_dir(subject, "airflow.db").touch()
            else:
                return original_popen(popen_args, *args, **kwargs)

            return handle_mock

        with mock.patch.object(
            subprocess, "Popen", side_effect=popen_mock
        ) as popen, mock.patch(
            "meltano.core.plugin_invoker.PluginConfigService.configure"
        ) as configure:
            invoker = plugin_invoker_factory(subject)
            # This ends up calling subject.before_configure
            with invoker.prepared(session):
                commands = [
                    popen_args[1]
                    for _, (popen_args, *_), kwargs in popen.mock_calls
                    if isinstance(popen_args, list)
                ]
                assert commands == ["--help", "initdb"]
                assert configure.call_count == 2

                assert run_dir.joinpath("airflow.cfg").exists()
                assert project.plugin_dir(subject, "airflow.db").exists()

                airflow_cfg = ConfigParser()
                with run_dir.joinpath("airflow.cfg").open() as cfg:
                    airflow_cfg.read_file(cfg)

                assert airflow_cfg["core"]["dags_folder"]

            assert not run_dir.joinpath("airflow.cfg").exists()
