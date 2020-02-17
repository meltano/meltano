import pytest
from configparser import ConfigParser
from unittest import mock


from meltano.core.plugin import PluginType
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.plugin.airflow import AirflowInvoker


AIRFLOW_CONFIG = """

"""


class TestAirflow:
    @pytest.fixture(scope="class")
    def subject(self, project_add_service):
        with mock.patch.object(
            PluginInstallService, "install_plugin"
        ) as install_plugin:
            return project_add_service.add(PluginType.ORCHESTRATORS, "airflow")

    def test_after_install(self, subject, project, session):
        handle_mock = mock.Mock()
        handle_mock.wait.return_value = 0

        def invoke_mock(*args, **kwargs):
            # first time, it creates the `airflow.cfg`
            if "--help" in args:
                airflow_cfg = ConfigParser()
                airflow_cfg["core"] = {"dummy": "dummy"}
                airflow_cfg["webserver"] = {"dummy": "dummy"}
                with project.run_dir("airflow", "airflow.cfg").open("w") as cfg:
                    airflow_cfg.write(cfg)

            # second time, it creates the `airflow.db`
            if "initdb" in args:
                project.plugin_dir(subject, "airflow.db").touch()

            return handle_mock

        # fmt: off
        with mock.patch.object(AirflowInvoker, "invoke", side_effect=invoke_mock) as invoke, \
          mock.patch("meltano.core.plugin_invoker.PluginConfigService.configure") as configure:
            subject.after_install(project)
            commands = [args[0]
                        for name, args, kwargs in invoke.mock_calls]
            assert commands == ["--help", "initdb"]
            assert configure.call_count == 2

            airflow_cfg = ConfigParser()
            with project.plugin_dir(subject, "airflow.cfg").open() as cfg:
                airflow_cfg.read_file(cfg)

            assert airflow_cfg['core']['dags_folder']
        # fmt: on
