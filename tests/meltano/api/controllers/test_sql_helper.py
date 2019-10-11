import pytest
from unittest import mock

from meltano.core.plugin import PluginType
from meltano.api.controllers.sql_helper import SqlHelper


@pytest.mark.usefixtures("session")
class TestSqlHelper:
    @pytest.fixture(scope="class")
    def project(self, project, project_add_service):
        # we have to use `postgres` because we only support two dialects
        project_add_service.add(PluginType.LOADERS, "target-postgres")
        project_add_service.add(PluginType.LOADERS, "target-sqlite")

        return project

    @pytest.fixture(scope="class")
    def subject(self):
        return SqlHelper()

    def test_get_db_engine_sqlite(
        self,
        app,
        subject,
        project,
        plugin_settings_service,
        elt_context_builder,
    ):
        sample_config = {"database": "pytest"}
        engine_uri = f"sqlite:///pytest.db"

        with mock.patch(
            "sqlalchemy.create_engine", return_value=None
        ) as create_engine_mock, mock.patch.object(
            plugin_settings_service, "as_config", return_value=sample_config
        ), mock.patch(
            "meltano.api.controllers.sql_helper.ELTContextBuilder",
            return_value=elt_context_builder,
        ):
            subject.get_db_engine("target-sqlite")
            create_engine_mock.assert_called_with(engine_uri)

    @mock.patch("meltano.api.controllers.sql_helper.listen")
    def test_get_db_engine_postgres(
        self,
        listen_mock,
        app,
        subject,
        plugin_settings_service,
        elt_context_builder,
    ):
        sample_config = {
            "user": "user",
            "password": "password",
            "host": "host",
            "port": "port",
            "dbname": "dbname",
        }

        engine_uri = "postgresql://user:password@host:port/dbname"

        with mock.patch(
            "sqlalchemy.create_engine", return_value=None
        ) as create_engine_mock, mock.patch.object(
            plugin_settings_service, "as_config", return_value=sample_config
        ), mock.patch(
            "meltano.api.controllers.sql_helper.ELTContextBuilder",
            return_value=elt_context_builder,
        ):
            subject.get_db_engine("target-postgres")

            assert listen_mock.called
            create_engine_mock.assert_called_with(engine_uri)
