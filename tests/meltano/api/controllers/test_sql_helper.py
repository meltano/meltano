import pytest
from unittest import mock

from meltano.core.plugin import PluginType
from meltano.api.controllers.sql_helper import SqlHelper


class TestSqlHelper:
    @pytest.fixture(scope="class")
    def project(self, project, project_add_service):
        postgresql = project_add_service.add(PluginType.CONNECTIONS, "postgresql")
        sqlite = project_add_service.add(PluginType.CONNECTIONS, "sqlite")

        return project

    @pytest.fixture(scope="class")
    def subject(self):
        return SqlHelper()

    @mock.patch("meltano.api.controllers.sql_helper.PluginSettingsService")
    def test_get_db_engine_sqlite(
        self, PluginSettingsServiceMock, app_context, subject, project
    ):
        instance = PluginSettingsServiceMock()
        instance.as_config.return_value = {"dbname": "dbname"}

        engine_uri = f"sqlite:///{project.root.joinpath('dbname')}.db"

        with mock.patch(
            "sqlalchemy.create_engine", return_value=None
        ) as create_engine_mock:
            subject.get_db_engine("sqlite")
            create_engine_mock.assert_called_with(engine_uri)

    @mock.patch("meltano.api.controllers.sql_helper.PluginSettingsService")
    @mock.patch("meltano.api.controllers.sql_helper.listen")
    def test_get_db_engine_postgres(
        self, listen_mock, PluginSettingsServiceMock, app_context, subject
    ):
        instance = PluginSettingsServiceMock()
        instance.as_config.return_value = {
            "user": "user",
            "password": "password",
            "host": "host",
            "port": "port",
            "dbname": "dbname",
        }

        engine_uri = "postgresql+psycopg2://user:password@host:port/dbname"

        with mock.patch(
            "sqlalchemy.create_engine", return_value=None
        ) as create_engine_mock:
            subject.get_db_engine("postgresql")

            assert listen_mock.called
            create_engine_mock.assert_called_with(engine_uri)
