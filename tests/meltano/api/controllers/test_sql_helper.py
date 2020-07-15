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
        self,
        app,
        subject,
        project,
        tap,
        plugin_settings_service_factory,
        elt_context_builder,
    ):
        plugin_settings_service = plugin_settings_service_factory(tap)

        sample_config = {"database": "pytest"}
        engine_uri = f"sqlite:///pytest.db"

        with mock.patch(
            "meltano.core.elt_context.PluginSettingsService",
            return_value=plugin_settings_service,
        ), mock.patch.object(
            plugin_settings_service, "as_dict", return_value=sample_config
        ), mock.patch.object(
            plugin_settings_service, "as_env", return_value={}
        ), mock.patch(
            "meltano.api.controllers.sql_helper.ELTContextBuilder",
            return_value=elt_context_builder,
        ):
            engine = subject.get_db_engine(tap.name, "target-sqlite", "skip")
            assert str(engine.url) == engine_uri

    @mock.patch("meltano.api.controllers.sql_helper.listen")
    def test_get_db_engine_postgres(
        self,
        listen_mock,
        app,
        subject,
        tap,
        plugin_settings_service_factory,
        elt_context_builder,
    ):
        plugin_settings_service = plugin_settings_service_factory(tap)
        sample_config = {
            "user": "user",
            "password": "password",
            "host": "host",
            "port": 5502,
            "dbname": "dbname",
            "schema": "tap_mock",
        }

        engine_uri = "postgresql://user:password@host:5502/dbname"

        with mock.patch(
            "meltano.core.elt_context.PluginSettingsService",
            return_value=plugin_settings_service,
        ), mock.patch.object(
            plugin_settings_service, "as_dict", return_value=sample_config
        ), mock.patch.object(
            plugin_settings_service, "as_env", return_value={}
        ), mock.patch(
            "meltano.api.controllers.sql_helper.ELTContextBuilder",
            return_value=elt_context_builder,
        ):
            engine = subject.get_db_engine(tap.name, "target-postgres", "skip")
            assert str(engine.url) == engine_uri

            assert listen_mock.called

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
