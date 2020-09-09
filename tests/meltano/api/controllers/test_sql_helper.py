import pytest
from unittest import mock

from meltano.core.plugin import PluginType, PluginRef
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
        target_sqlite = PluginRef(PluginType.LOADERS, "target-sqlite")
        plugin_settings_service = plugin_settings_service_factory(target_sqlite)
        plugin_settings_service.set("database", "pytest")

        config = plugin_settings_service.as_dict()
        engine_uri = f"sqlite:///{config['database']}.db"

        with mock.patch(
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
        target_postgres = PluginRef(PluginType.LOADERS, "target-postgres")
        plugin_settings_service = plugin_settings_service_factory(target_postgres)
        plugin_settings_service.set("user", "user")
        plugin_settings_service.set("password", "password")
        plugin_settings_service.set("host", "host")
        plugin_settings_service.set("port", 5502)
        plugin_settings_service.set("dbname", "dbname")

        config = plugin_settings_service.as_dict()
        engine_uri = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['dbname']}"

        with mock.patch(
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
