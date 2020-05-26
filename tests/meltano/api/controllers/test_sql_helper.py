import pytest
from unittest import mock

from meltano.core.plugin import PluginType
from meltano.api.controllers.sql_helper import SqlHelper, UnsupportedConnectionDialect


@pytest.mark.usefixtures("session")
class TestSqlHelper:
    @pytest.fixture(scope="class")
    def project(self, project, project_add_service):
        # we have to use `postgres` because we only support two dialects
        project_add_service.add(PluginType.LOADERS, "target-postgres")
        project_add_service.add(PluginType.LOADERS, "target-sqlite")
        project_add_service.add(PluginType.LOADERS, "target-snowflake")
        project_add_service.add(PluginType.LOADERS, "target-csv")

        return project

    @pytest.fixture(scope="class")
    def subject(self):
        return SqlHelper()

    def test_get_db_engine_sqlite(
        self, app, subject, project, tap, plugin_settings_service, elt_context_builder
    ):
        sample_config = {"database": "pytest"}
        engine_uri = f"sqlite:///pytest.db"

        with mock.patch(
            "sqlalchemy.create_engine", return_value=None
        ) as create_engine_mock, mock.patch.object(
            plugin_settings_service,
            "with_env_override",
            return_value=plugin_settings_service,
        ), mock.patch.object(
            plugin_settings_service, "as_config", return_value=sample_config
        ), mock.patch.object(
            plugin_settings_service, "as_env", return_value={}
        ), mock.patch(
            "meltano.api.controllers.sql_helper.ELTContextBuilder",
            return_value=elt_context_builder,
        ):
            subject.get_db_engine(tap.name, "target-sqlite", "skip")
            create_engine_mock.assert_called_with(engine_uri)

    @mock.patch("meltano.api.controllers.sql_helper.listen")
    def test_get_db_engine_postgres(
        self,
        listen_mock,
        app,
        subject,
        tap,
        plugin_settings_service,
        elt_context_builder,
    ):
        sample_config = {
            "user": "user",
            "password": "password",
            "host": "host",
            "port": "port",
            "dbname": "dbname",
            "schema": "tap_mock",
        }

        engine_uri = "postgresql://user:password@host:port/dbname"

        with mock.patch(
            "sqlalchemy.create_engine", return_value=None
        ) as create_engine_mock, mock.patch.object(
            plugin_settings_service,
            "with_env_override",
            return_value=plugin_settings_service,
        ), mock.patch.object(
            plugin_settings_service, "as_config", return_value=sample_config
        ), mock.patch.object(
            plugin_settings_service, "as_env", return_value={}
        ), mock.patch(
            "meltano.api.controllers.sql_helper.ELTContextBuilder",
            return_value=elt_context_builder,
        ):
            subject.get_db_engine(tap.name, "target-postgres", "skip")

            assert listen_mock.called
            create_engine_mock.assert_called_with(engine_uri)

    @pytest.mark.parametrize("loader", ["target-csv", "target-snowflake"])
    def test_get_db_engine_unsupported(
        self, app, subject, tap, loader, elt_context_builder
    ):
        with mock.patch(
            "meltano.api.controllers.sql_helper.ELTContextBuilder",
            return_value=elt_context_builder,
        ):
            with pytest.raises(UnsupportedConnectionDialect):
                subject.get_db_engine(tap.name, loader, "skip")
