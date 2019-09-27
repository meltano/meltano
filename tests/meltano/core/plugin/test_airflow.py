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
                project.run_dir("airflow", "airflow.cfg").touch()

            # second time, it creates the `airflow.db`
            if "initdb" in args:
                project.plugin_dir(subject, "airflow.db").touch()

            return handle_mock

        # fmt: off
        with mock.patch.object(AirflowInvoker, "invoke", side_effect=invoke_mock) as invoke, \
          mock.patch("meltano.core.plugin_invoker.PluginConfigService.configure") as configure, \
          mock.patch.object(ConfigParser, "__getitem__") as get_config_item, \
          mock.patch.object(ConfigParser, "write") as config_write:
            subject.after_install(project)
            commands = [args[0]
                        for name, args, kwargs in invoke.mock_calls]
            assert commands == ["--help", "initdb"]
            assert configure.call_count == 2
        # fmt: on
