from contextlib import contextmanager
from datetime import date, datetime
from unittest import mock

import dotenv
import pytest
from meltano.core.plugin import PluginRef, PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin.settings_service import (
    REDACTED_VALUE,
    PluginSettingsService,
    SettingValueStore,
)
from meltano.core.project_plugins_service import PluginAlreadyAddedException
from meltano.core.setting import Setting


def test_create(session):
    setting = Setting(
        name="api_key.test.test", namespace="gitlab", value="C4F3C4F3", enabled=True
    )

    session.add(setting)
    session.commit()

    fetched = session.query(Setting).first()
    assert setting == fetched


@pytest.fixture(scope="class")
def env_var(plugin_discovery_service):
    def _wrapper(plugin_settings_service, setting_name):
        setting_def = plugin_settings_service.find_setting(setting_name)
        return plugin_settings_service.setting_env(setting_def)

    return _wrapper


@pytest.fixture(scope="class")
def custom_tap(project_add_service):
    EXPECTED = {"test": "custom", "start_date": None, "secure": None}
    tap = ProjectPlugin(
        PluginType.EXTRACTORS,
        name="tap-custom",
        namespace="tap_custom",
        config=EXPECTED,
    )
    try:
        return project_add_service.add_plugin(tap)
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture
def subject(session, project_add_service, tap, plugin_settings_service_factory):
    try:
        project_add_service.add("extractors", tap.name)
    except PluginAlreadyAddedException:
        pass

    return plugin_settings_service_factory(tap)


class TestPluginSettingsService:
    def test_get_with_source(
        self,
        session,
        subject,
        project,
        tap,
        env_var,
        monkeypatch,
        config_service,
        plugin_settings_service_factory,
    ):
        # returns the default value when unset
        assert subject.get_with_source("test", session=session) == (
            "mock",
            SettingValueStore.DEFAULT,
        )

        # overriden by an Setting db value when set
        subject.set(
            "test", "THIS_IS_FROM_DB", store=SettingValueStore.DB, session=session
        )

        assert subject.get_with_source("test", session=session) == (
            "THIS_IS_FROM_DB",
            SettingValueStore.DB,
        )

        # overriden via the `meltano.yml` configuration
        subject.set("test", 42, store=SettingValueStore.MELTANO_YML, session=session)

        assert subject.get_with_source("test", session=session) == (
            42,
            SettingValueStore.MELTANO_YML,
        )

        # revert back to the original
        subject.reset(store=SettingValueStore.MELTANO_YML)

        # overriden via ENV
        monkeypatch.setenv(env_var(subject, "test"), "N33DC0F33")

        assert subject.get_with_source("test", session=session) == (
            "N33DC0F33",
            SettingValueStore.ENV,
        )

        # overridden via config override
        monkeypatch.setitem(subject.config_override, "test", "foo")

        assert subject.get_with_source("test", session=session) == (
            "foo",
            SettingValueStore.CONFIG_OVERRIDE,
        )

        # Verify that integer settings set in env are cast correctly
        monkeypatch.setenv(env_var(subject, "port"), "3333")

        assert subject.get_with_source("port", session=session) == (
            3333,
            SettingValueStore.ENV,
        )

        # Verify that array settings set in env are cast correctly
        monkeypatch.setenv(env_var(subject, "list"), '[1, 2, 3, "4"]')

        assert subject.get_with_source("list", session=session) == (
            [1, 2, 3, "4"],
            SettingValueStore.ENV,
        )

        # Verify that object settings set in env are cast correctly
        monkeypatch.setenv(env_var(subject, "object"), '{"1":{"2":3}}')

        assert subject.get_with_source("object", session=session) == (
            {"1": {"2": 3}},
            SettingValueStore.ENV,
        )

        # Verify that boolean settings set in env are cast correctly
        # Default
        assert subject.get_with_source("boolean", session=session) == (
            None,
            SettingValueStore.DEFAULT,
        )

        # Negated alias
        monkeypatch.setenv("TAP_MOCK_DISABLED", "true")

        assert subject.get_with_source("boolean", session=session) == (
            False,
            SettingValueStore.ENV,
        )

        # Regular alias
        monkeypatch.setenv("TAP_MOCK_ENABLED", "on")

        assert subject.get_with_source("boolean", session=session) == (
            True,
            SettingValueStore.ENV,
        )

        # Preferred env var
        monkeypatch.setenv(env_var(subject, "boolean"), "0")

        assert subject.get_with_source("boolean", session=session) == (
            False,
            SettingValueStore.ENV,
        )

    def test_definitions(self, subject, monkeypatch):
        subject.show_hidden = False
        subject._setting_defs = None

        setting_defs_by_name = {s.name: s for s in subject.definitions()}

        # Regular settings
        assert "test" in setting_defs_by_name
        assert "start_date" in setting_defs_by_name

        # Expect hidden
        assert "secret" not in setting_defs_by_name

    def test_as_dict(self, subject, session, tap):
        EXPECTED = {"test": "mock", "start_date": None, "secure": None}
        full_config = subject.as_dict(session=session)
        redacted_config = subject.as_dict(redacted=True, session=session)

        for k, v in EXPECTED.items():
            assert full_config.get(k) == v
            assert redacted_config.get(k) == v

    def test_as_dict_process(self, subject, tap):
        config = subject.as_dict()
        assert config["auth.username"] is None
        assert config["auth.password"] is None
        assert "auth" not in config

        config = subject.as_dict(process=True)
        assert "auth.username" not in config
        assert "auth.password" not in config
        assert "auth" not in config

        subject.set("auth.username", "nested_username")

        config = subject.as_dict()
        assert config["auth.username"] == "nested_username"
        assert config["auth.password"] is None
        assert "auth" not in config

        config = subject.as_dict(process=True)
        assert config["auth"]["username"] == "nested_username"
        assert "password" not in config["auth"]
        assert "auth.username" not in config
        assert "auth.password" not in config

        subject.set("auth.password", "nested_password")

        config = subject.as_dict()
        assert config["auth.username"] == "nested_username"
        assert config["auth.password"] == "nested_password"
        assert "auth" not in config

        config = subject.as_dict(process=True)
        assert config["auth"]["username"] == "nested_username"
        assert config["auth"]["password"] == "nested_password"
        assert "auth.username" not in config
        assert "auth.password" not in config

    def test_as_dict_custom(
        self, session, project, custom_tap, plugin_settings_service_factory
    ):
        subject = plugin_settings_service_factory(custom_tap)
        assert subject.as_dict(extras=False, session=session) == custom_tap.config

    def test_as_dict_redacted(self, subject, session, tap):
        store = SettingValueStore.DB

        # ensure values are redacted when they are set
        subject.set("secure", "thisisatest", store=store, session=session)
        config = subject.as_dict(redacted=True, session=session)

        assert config["secure"] == REDACTED_VALUE

        # although setting the REDACTED_VALUE does nothing
        subject.set("secure", REDACTED_VALUE, store=store, session=session)
        config = subject.as_dict(session=session)
        assert config["secure"] == "thisisatest"

    def test_as_env(self, subject, session, tap, env_var):
        subject.set("boolean", True, store=SettingValueStore.DOTENV)
        subject.set("list", [1, 2, 3, "4"], store=SettingValueStore.DOTENV)
        subject.set("object", {"1": {"2": 3}}, store=SettingValueStore.DOTENV)

        config = subject.as_env(session=session)
        subject.reset(store=SettingValueStore.DOTENV)

        # Settings with values are present
        assert config[env_var(subject, "test")] == "mock"
        assert config[env_var(subject, "list")] == '[1, 2, 3, "4"]'
        assert config[env_var(subject, "object")] == '{"1": {"2": 3}}'
        assert config[env_var(subject, "boolean")] == "true"

        # Settings without values are not
        assert env_var(subject, "start_date") not in config
        assert env_var(subject, "secure") not in config

        # Env aliases are present
        assert config["TAP_MOCK_ENABLED"] == "true"

        # Negated aliases are not
        assert "TAP_MOCK_DISABLED" not in config

        # Generic env vars are present
        assert config["MELTANO_EXTRACT_TEST"] == "mock"
        assert config["MELTANO_EXTRACT_LIST"] == '[1, 2, 3, "4"]'
        assert config["MELTANO_EXTRACT_OBJECT"] == '{"1": {"2": 3}}'
        assert config["MELTANO_EXTRACT_BOOLEAN"] == "true"

    def test_as_env_custom(
        self, project, session, custom_tap, env_var, plugin_settings_service_factory
    ):
        subject = plugin_settings_service_factory(custom_tap)
        config = subject.as_env(session=session)
        for k, v in custom_tap.config.items():
            assert config.get(env_var(subject, k)) == v

    def test_namespace_as_env_prefix(
        self, project, session, target, env_var, plugin_settings_service_factory
    ):
        subject = plugin_settings_service_factory(target)

        def assert_env_value(value, env_var):
            value, metadata = subject.get_with_metadata("schema")
            assert value == value
            assert metadata["env_var"] == env_var

        assert subject.get("schema") is None

        subject.set("schema", "default", store=SettingValueStore.DOTENV)
        value, metadata = subject.get_with_metadata("schema")

        # Custom `env` is the default
        assert_env_value("default", "MOCKED_SCHEMA")

        subject.unset("schema")

        # Namespace prefix
        dotenv.set_key(project.dotenv, "MOCK_SCHEMA", "namespace_prefix")
        assert_env_value("namespace_prefix", "MOCK_SCHEMA")

        # Name prefix
        dotenv.set_key(project.dotenv, "TARGET_MOCK_SCHEMA", "name_prefix")
        assert_env_value("name_prefix", "TARGET_MOCK_SCHEMA")

        # Custom `env`
        dotenv.set_key(project.dotenv, "MOCKED_SCHEMA", "custom_env")
        assert_env_value("custom_env", "MOCKED_SCHEMA")

        config = subject.as_env(session=session)
        subject.reset(store=SettingValueStore.DOTENV)

        assert (
            config["MOCKED_SCHEMA"]  # Custom `env`
            == config["TARGET_MOCK_SCHEMA"]  # Name prefix
            == config["MOCK_SCHEMA"]  # Namespace prefix
            == config["MELTANO_LOAD_SCHEMA"]  # Generic prefix, read-only
            == "custom_env"
        )

    def test_store_db(self, session, subject, tap):
        store = SettingValueStore.DB

        subject.set("test_a", "THIS_IS_FROM_DB", store=store, session=session)
        subject.set("test_b", "THIS_IS_FROM_DB", store=store, session=session)

        assert session.query(Setting).count() == 2

        subject.unset("test_a", store=store, session=session)

        assert session.query(Setting).count() == 1

        subject.reset(store=store, session=session)

        assert session.query(Setting).count() == 0

    def test_store_meltano_yml(self, subject, project, tap):
        store = SettingValueStore.MELTANO_YML

        subject.set("test_a", "THIS_IS_FROM_YML", store=store)
        subject.set("test_b", "THIS_IS_FROM_YML", store=store)

        with project.meltano_update() as meltano:
            extractor = meltano.plugins.extractors[0]
            assert extractor.config["test_a"] == "THIS_IS_FROM_YML"
            assert extractor.config["test_b"] == "THIS_IS_FROM_YML"

        subject.unset("test_a", store=store)

        with project.meltano_update() as meltano:
            extractor = meltano.plugins.extractors[0]
            assert "test_a" not in extractor.config
            assert extractor.config["test_b"] == "THIS_IS_FROM_YML"

        subject.reset(store=store)

        with project.meltano_update() as meltano:
            extractor = meltano.plugins.extractors[0]
            assert "test_a" not in extractor.config
            assert "test_b" not in extractor.config

    def test_store_dotenv(self, subject, project, tap):
        store = SettingValueStore.DOTENV

        assert not project.dotenv.exists()

        subject.set("test", "THIS_IS_FROM_DOTENV", store=store)
        subject.set("start_date", "THIS_IS_FROM_DOTENV", store=store)

        dotenv_contents = dotenv.dotenv_values(project.dotenv)
        assert dotenv_contents["TAP_MOCK_TEST"] == "THIS_IS_FROM_DOTENV"
        assert dotenv_contents["TAP_MOCK_START_DATE"] == "THIS_IS_FROM_DOTENV"
        assert subject.get_with_source("test") == (
            "THIS_IS_FROM_DOTENV",
            SettingValueStore.DOTENV,
        )
        assert subject.get_with_source("start_date") == (
            "THIS_IS_FROM_DOTENV",
            SettingValueStore.DOTENV,
        )

        dotenv.set_key(project.dotenv, "TAP_MOCK_DISABLED", "true")
        dotenv.set_key(project.dotenv, "TAP_MOCK_ENABLED", "false")
        assert subject.get_with_source("boolean") == (False, SettingValueStore.DOTENV)

        subject.set("boolean", True, store=store)

        dotenv_contents = dotenv.dotenv_values(project.dotenv)
        assert dotenv_contents["TAP_MOCK_BOOLEAN"] == "true"
        assert "TAP_MOCK_DISABLED" not in dotenv_contents
        assert "TAP_MOCK_ENABLED" not in dotenv_contents
        assert subject.get_with_source("boolean") == (True, SettingValueStore.DOTENV)

        subject.set("list", [1, 2, 3, "4"], store=store)

        dotenv_contents = dotenv.dotenv_values(project.dotenv)
        assert dotenv_contents["TAP_MOCK_LIST"] == '[1, 2, 3, "4"]'
        assert subject.get_with_source("list") == (
            [1, 2, 3, "4"],
            SettingValueStore.DOTENV,
        )

        subject.set("object", {"1": {"2": 3}}, store=store)

        dotenv_contents = dotenv.dotenv_values(project.dotenv)
        assert dotenv_contents["TAP_MOCK_OBJECT"] == '{"1": {"2": 3}}'
        assert subject.get_with_source("object") == (
            {"1": {"2": 3}},
            SettingValueStore.DOTENV,
        )

        subject.unset("test", store=store)

        dotenv_contents = dotenv.dotenv_values(project.dotenv)
        assert "TAP_MOCK_TEST" not in dotenv_contents
        assert dotenv_contents["TAP_MOCK_START_DATE"] == "THIS_IS_FROM_DOTENV"
        assert dotenv_contents["TAP_MOCK_BOOLEAN"] == "true"

        subject.reset(store=store)
        assert not project.dotenv.exists()

    def test_env_var_expansion(
        self, session, subject, project, tap, monkeypatch, env_var
    ):
        monkeypatch.setenv("VAR", "hello world!")
        monkeypatch.setenv("FOO", "42")

        project.dotenv.touch()
        dotenv.set_key(project.dotenv, "A", "rock")
        dotenv.set_key(project.dotenv, "B", "paper")
        dotenv.set_key(project.dotenv, "C", "scissors")

        yml_config = {
            "var": "$VAR",
            "foo": "${FOO}",
            "missing": "$MISSING",
            "multiple": "$A ${B} $C",
            "info": "$MELTANO_EXTRACTOR_NAME",
            "_extra": "$TAP_MOCK_MULTIPLE",
            "_extra_generic": "$MELTANO_EXTRACT_FOO",
        }
        monkeypatch.setattr(subject.plugin, "config", yml_config)

        # Env vars inside env var values do not get expanded
        monkeypatch.setenv(env_var(subject, "test"), "$FOO")

        config = subject.as_dict(session=session)

        assert config["var"] == "hello world!"
        assert config["foo"] == "42"
        assert config["missing"] == None
        assert config["multiple"] == "rock paper scissors"
        assert config["info"] == "tap-mock"

        # Values of extras can reference regular settings
        assert config["_extra"] == config["multiple"]
        assert config["_extra_generic"] == config["foo"]

        # Env vars inside env var values do not get expanded
        assert config["test"] == "$FOO"

        # Expansion can be disabled
        config = subject.as_dict(session=session, expand_env_vars=False)
        assert {k: v for k, v in config.items() if k in yml_config} == yml_config

    def test_nested_keys(self, session, subject, project, tap):
        def set_config(path, value):
            subject.set(path, value, store=SettingValueStore.MELTANO_YML)

        def unset_config(path):
            subject.unset(path, store=SettingValueStore.MELTANO_YML)

        def yml_config():
            with project.meltano_update() as meltano:
                extractor = meltano.plugins.extractors[0]
                return extractor.config

        def final_config():
            return subject.as_dict(session=session)

        set_config("metadata.stream.replication-key", "created_at")

        assert yml_config()["metadata.stream.replication-key"] == "created_at"
        assert final_config()["metadata.stream.replication-key"] == "created_at"

        set_config(["metadata", "stream", "replication-key"], "created_at")

        yml = yml_config()
        assert "metadata.stream.replication-key" not in yml
        assert yml["metadata"]["stream"]["replication-key"] == "created_at"
        assert final_config()["metadata.stream.replication-key"] == "created_at"

        set_config(["metadata", "stream", "replication-method"], "INCREMENTAL")

        yml = yml_config()
        assert "metadata.stream.replication-key" not in yml
        assert "metadata.stream.replication-method" not in yml
        assert yml["metadata"]["stream"]["replication-key"] == "created_at"
        assert yml["metadata"]["stream"]["replication-method"] == "INCREMENTAL"
        final = final_config()
        assert final["metadata.stream.replication-key"] == "created_at"
        assert final["metadata.stream.replication-method"] == "INCREMENTAL"

        set_config(["metadata.stream.replication-key"], "created_at")
        unset_config(["metadata.stream.replication-method"])

        yml = yml_config()
        assert "metadata" not in yml
        assert yml["metadata.stream.replication-key"] == "created_at"
        assert final_config()["metadata.stream.replication-key"] == "created_at"

        set_config(["metadata", "stream.replication-key"], "created_at")

        yml = yml_config()
        assert "metadata.stream.replication-key" not in yml
        assert yml["metadata"]["stream.replication-key"] == "created_at"
        assert final_config()["metadata.stream.replication-key"] == "created_at"

        unset_config(["metadata", "stream.replication-key"])

        yml = yml_config()
        assert "metadata.stream.replication-key" not in yml
        assert "metadata" not in yml
        assert "metadata.stream.replication-key" not in final_config()

    def test_custom_setting(self, session, subject, tap, env_var):
        subject.set("custom_string", "from_yml", store=SettingValueStore.MELTANO_YML)
        subject.set("custom_bool", True, store=SettingValueStore.MELTANO_YML)
        subject.set("custom_array", [1, 2, 3, "4"], store=SettingValueStore.MELTANO_YML)

        assert subject.get_with_source("custom_string", session=session) == (
            "from_yml",
            SettingValueStore.MELTANO_YML,
        )
        assert subject.get_with_source("custom_bool", session=session) == (
            True,
            SettingValueStore.MELTANO_YML,
        )
        assert subject.get_with_source("custom_array", session=session) == (
            [1, 2, 3, "4"],
            SettingValueStore.MELTANO_YML,
        )

        subject.env_override = {
            env_var(subject, "custom_string"): "from_env",
            env_var(subject, "custom_bool"): "off",
            env_var(subject, "custom_array"): '["foo"]',
        }

        assert subject.get_with_source("custom_string", session=session) == (
            "from_env",
            SettingValueStore.ENV,
        )
        assert subject.get_with_source("custom_bool", session=session) == (
            False,
            SettingValueStore.ENV,
        )
        assert subject.get_with_source("custom_array", session=session) == (
            ["foo"],
            SettingValueStore.ENV,
        )

    def test_date_values(self, subject, monkeypatch):
        today = date.today()
        monkeypatch.setitem(subject.plugin.config, "start_date", today)
        assert subject.get("start_date") == today.isoformat()

        now = datetime.now()
        monkeypatch.setitem(subject.plugin.config, "start_date", now)
        assert subject.get("start_date") == now.isoformat()

    def test_kind_object(self, subject, tap, monkeypatch, env_var):
        assert subject.get_with_source("object") == (
            {"nested": "from_default"},
            SettingValueStore.DEFAULT,
        )

        subject.set("object.username", "from_meltano_yml")

        assert subject.get_with_source("object") == (
            {"username": "from_meltano_yml"},
            SettingValueStore.MELTANO_YML,
        )

        subject.set("data.password", "from_meltano_yml_alias")

        assert subject.get_with_source("object") == (
            {"username": "from_meltano_yml", "password": "from_meltano_yml_alias"},
            SettingValueStore.MELTANO_YML,
        )

        subject.set(["object", "password"], "from_meltano_yml")

        assert subject.get_with_source("object") == (
            {"username": "from_meltano_yml", "password": "from_meltano_yml"},
            SettingValueStore.MELTANO_YML,
        )

        subject.set(["object", "deep", "nesting"], "from_meltano_yml")

        assert subject.get_with_source("object") == (
            {
                "username": "from_meltano_yml",
                "password": "from_meltano_yml",
                "deep.nesting": "from_meltano_yml",
            },
            SettingValueStore.MELTANO_YML,
        )

        monkeypatch.setenv(env_var(subject, "object.deep.nesting"), "from_env")

        assert subject.get_with_source("object") == (
            {
                "username": "from_meltano_yml",
                "password": "from_meltano_yml",
                "deep.nesting": "from_env",
            },
            SettingValueStore.ENV,
        )

        monkeypatch.setenv(env_var(subject, "data"), '{"foo":"from_env_alias"}')

        assert subject.get_with_source("object") == (
            {"foo": "from_env_alias"},
            SettingValueStore.ENV,
        )

        monkeypatch.setenv(env_var(subject, "object"), '{"foo":"from_env"}')

        assert subject.get_with_source("object") == (
            {"foo": "from_env"},
            SettingValueStore.ENV,
        )

    def test_extra(self, subject, tap, monkeypatch, env_var):
        subject._setting_defs = None

        assert "_select" in subject.as_dict()
        assert "_select" in subject.as_dict(extras=True)
        assert "_select" not in subject.as_dict(extras=False)

        assert subject.get_with_source("_select") == (
            ["*.*"],
            SettingValueStore.DEFAULT,
        )

        monkeypatch.setitem(
            subject.plugin.parent._variant.extras, "select", ["from_default"]
        )
        subject._setting_defs = None

        assert subject.get_with_source("_select") == (
            ["from_default"],
            SettingValueStore.DEFAULT,
        )

        monkeypatch.setitem(
            subject.plugin.config, "_select", ["from_meltano_yml_config"]
        )

        assert subject.get_with_source("_select") == (
            ["from_meltano_yml_config"],
            SettingValueStore.MELTANO_YML,
        )

        monkeypatch.setitem(subject.plugin.extras, "select", ["from_meltano_yml_extra"])

        assert subject.get_with_source("_select") == (
            ["from_meltano_yml_extra"],
            SettingValueStore.MELTANO_YML,
        )

        subject.set("_select", ["from_meltano_yml"])

        assert subject.get_with_source("_select") == (
            ["from_meltano_yml"],
            SettingValueStore.MELTANO_YML,
        )

        subject.unset("_select")

        assert subject.get_with_source("_select") == (
            ["from_default"],
            SettingValueStore.DEFAULT,
        )

        monkeypatch.setenv(env_var(subject, "_select"), '["from_env"]')

        assert subject.get_with_source("_select") == (
            ["from_env"],
            SettingValueStore.ENV,
        )

    def test_extra_object(
        self,
        subject,
        monkeypatch,
        env_var,
        project_add_service,
        plugin_settings_service_factory,
    ):
        try:
            transform = project_add_service.add(
                PluginType.TRANSFORMS, "tap-mock-transform"
            )
        except PluginAlreadyAddedException as err:
            transform = err.plugin

        subject = plugin_settings_service_factory(transform)
        assert "_vars" in subject.as_dict()
        assert "_vars" in subject.as_dict(extras=True)
        assert "_vars" not in subject.as_dict(extras=False)

        assert subject.get_with_source("_vars") == ({}, SettingValueStore.DEFAULT)

        monkeypatch.setitem(
            subject.plugin.parent._variant.extras,
            "vars",
            {"var": "from_default", "other": "from_default"},
        )
        subject._setting_defs = None

        assert subject.get_with_source("_vars") == (
            {"var": "from_default", "other": "from_default"},
            SettingValueStore.DEFAULT,
        )

        monkeypatch.setitem(subject.plugin.extras, "vars", {"var": "from_meltano_yml"})

        assert subject.get_with_source("_vars") == (
            {"var": "from_meltano_yml", "other": "from_default"},
            SettingValueStore.MELTANO_YML,
        )

        subject.set("_vars", {"other": "from_meltano_yml"})

        assert subject.get_with_source("_vars") == (
            {"var": "from_default", "other": "from_meltano_yml"},
            SettingValueStore.MELTANO_YML,
        )

        monkeypatch.setenv(env_var(subject, "_vars.var"), "from_env")

        assert subject.get_with_source("_vars") == (
            {"var": "from_env", "other": "from_meltano_yml"},
            SettingValueStore.ENV,
        )

        monkeypatch.setenv(env_var(subject, "_vars"), '{"var": "from_env"}')

        assert subject.get_with_source("_vars") == (
            {"var": "from_env"},
            SettingValueStore.ENV,
        )
