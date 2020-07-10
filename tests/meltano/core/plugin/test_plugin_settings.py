import pytest
import dotenv
from contextlib import contextmanager

from meltano.core.config_service import PluginAlreadyAddedException
from meltano.core.setting import Setting
from meltano.core.plugin import PluginRef, PluginType, PluginInstall
from meltano.core.plugin.settings_service import (
    PluginSettingsService,
    SettingValueSource,
    SettingValueStore,
    REDACTED_VALUE,
)


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
def custom_tap(config_service):
    EXPECTED = {"test": "custom", "start_date": None, "secure": None}
    tap = PluginInstall(
        PluginType.EXTRACTORS,
        name="tap-custom",
        namespace="tap_custom",
        config=EXPECTED,
    )
    try:
        return config_service.add_to_file(tap)
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
        profile = tap.add_profile("profile", label="Profile")
        config_service.update_plugin(tap)
        tap_with_profile = config_service.find_plugin(tap.name)
        tap_with_profile.use_profile(profile)
        subject_with_profile = plugin_settings_service_factory(tap_with_profile)

        # returns the default value when unset
        assert subject.get_with_source("test", session=session) == (
            "mock",
            SettingValueSource.DEFAULT,
        )
        assert subject_with_profile.get_with_source("test", session=session) == (
            "mock",
            SettingValueSource.DEFAULT,
        )

        # overriden by an Setting db value when set
        subject.set("test", "THIS_IS_FROM_DB", session=session)
        subject_with_profile.set(
            "test", "THIS_IS_FROM_DB_WITH_PROFILE", session=session
        )

        assert subject.get_with_source("test", session=session) == (
            "THIS_IS_FROM_DB",
            SettingValueSource.DB,
        )
        assert subject_with_profile.get_with_source("test", session=session) == (
            "THIS_IS_FROM_DB_WITH_PROFILE",
            SettingValueSource.DB,
        )

        # overriden via the `meltano.yml` configuration
        subject.set("test", 42, store=SettingValueStore.MELTANO_YML, session=session)
        subject_with_profile.set(
            "test", 43, store=SettingValueStore.MELTANO_YML, session=session
        )

        assert subject.get_with_source("test", session=session) == (
            42,
            SettingValueSource.MELTANO_YML,
        )
        assert subject_with_profile.get_with_source("test", session=session) == (
            43,
            SettingValueSource.MELTANO_YML,
        )

        # revert back to the original
        subject.reset(store=SettingValueStore.MELTANO_YML)
        subject_with_profile.reset(store=SettingValueStore.MELTANO_YML)

        # overriden via ENV
        monkeypatch.setenv(env_var(subject, "test"), "N33DC0F33")

        assert subject.get_with_source("test", session=session) == (
            "N33DC0F33",
            SettingValueSource.ENV,
        )
        assert subject_with_profile.get_with_source("test", session=session) == (
            "N33DC0F33",
            SettingValueSource.ENV,
        )

        # overridden via config override
        monkeypatch.setitem(subject.config_override, "test", "foo")
        monkeypatch.setitem(subject_with_profile.config_override, "test", "foo")

        assert subject.get_with_source("test", session=session) == (
            "foo",
            SettingValueSource.CONFIG_OVERRIDE,
        )
        assert subject_with_profile.get_with_source("test", session=session) == (
            "foo",
            SettingValueSource.CONFIG_OVERRIDE,
        )

        # Verify that integer settings set in env are cast correctly
        monkeypatch.setenv(env_var(subject, "port"), "3333")

        assert subject.get_with_source("port", session=session) == (
            3333,
            SettingValueSource.ENV,
        )

        # Verify that boolean settings set in env are cast correctly
        # Default
        assert subject.get_with_source("boolean", session=session) == (
            None,
            SettingValueSource.DEFAULT,
        )

        # Negated alias
        monkeypatch.setenv("TAP_MOCK_DISABLED", "true")

        assert subject.get_with_source("boolean", session=session) == (
            False,
            SettingValueSource.ENV,
        )

        # Regular alias
        monkeypatch.setenv("TAP_MOCK_ENABLED", "on")

        assert subject.get_with_source("boolean", session=session) == (
            True,
            SettingValueSource.ENV,
        )

        # Preferred env var
        monkeypatch.setenv(env_var(subject, "boolean"), "0")

        assert subject.get_with_source("boolean", session=session) == (
            False,
            SettingValueSource.ENV,
        )

    def test_as_dict(self, subject, session, tap):
        EXPECTED = {"test": "mock", "start_date": None, "secure": None}
        full_config = subject.as_dict(session=session)
        redacted_config = subject.as_dict(redacted=True, session=session)

        for k, v in EXPECTED.items():
            assert full_config.get(k) == v
            assert redacted_config.get(k) == v

    def test_as_dict_custom(
        self, session, project, custom_tap, plugin_settings_service_factory
    ):
        subject = plugin_settings_service_factory(custom_tap)
        assert subject.as_dict(session=session) == custom_tap.config

    def test_as_dict_redacted(self, subject, session, tap):
        # ensure values are redacted when they are set
        subject.set("secure", "thisisatest", session=session)
        config = subject.as_dict(redacted=True, session=session)

        assert config["secure"] == REDACTED_VALUE

        # although setting the REDACTED_VALUE does nothing
        subject.set("secure", REDACTED_VALUE, session=session)
        config = subject.as_dict(session=session)
        assert config["secure"] == "thisisatest"

    def test_as_env(self, subject, session, tap, env_var):
        config = subject.as_env(session=session)

        assert config.get(env_var(subject, "test")) == "mock"
        assert config.get(env_var(subject, "start_date")) == None
        assert config.get(env_var(subject, "secure")) == None

    def test_as_env_custom(
        self, project, session, custom_tap, env_var, plugin_settings_service_factory
    ):
        subject = plugin_settings_service_factory(custom_tap)
        config = subject.as_env(session=session)
        for k, v in custom_tap.config.items():
            assert config.get(env_var(subject, k)) == v

    def test_store_db(self, session, subject, tap):
        subject.set("test_a", "THIS_IS_FROM_DB", session=session)
        subject.set("test_b", "THIS_IS_FROM_DB", session=session)

        assert session.query(Setting).count() == 2

        subject.unset("test_a", session=session)

        assert session.query(Setting).count() == 1

        subject.reset(session=session)

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
            SettingValueSource.DOTENV,
        )
        assert subject.get_with_source("start_date") == (
            "THIS_IS_FROM_DOTENV",
            SettingValueSource.DOTENV,
        )

        dotenv.set_key(project.dotenv, "TAP_MOCK_DISABLED", "true")
        dotenv.set_key(project.dotenv, "TAP_MOCK_ENABLED", "false")
        assert subject.get_with_source("boolean") == (False, SettingValueSource.DOTENV)

        subject.set("boolean", True, store=store)

        dotenv_contents = dotenv.dotenv_values(project.dotenv)
        assert dotenv_contents["TAP_MOCK_BOOLEAN"] == "True"
        assert "TAP_MOCK_DISABLED" not in dotenv_contents
        assert "TAP_MOCK_ENABLED" not in dotenv_contents
        assert subject.get_with_source("boolean") == (True, SettingValueSource.DOTENV)

        subject.unset("test", store=store)

        dotenv_contents = dotenv.dotenv_values(project.dotenv)
        assert "TAP_MOCK_TEST" not in dotenv_contents
        assert dotenv_contents["TAP_MOCK_START_DATE"] == "THIS_IS_FROM_DOTENV"
        assert dotenv_contents["TAP_MOCK_BOOLEAN"] == "True"

        subject.reset(store=store)
        assert not project.dotenv.exists()

    def test_env_var_substitution(self, session, subject, project, tap):
        with project.meltano_update() as meltano:
            extractor = meltano.plugins.extractors[0]
            extractor.config = {
                "var": "$VAR",
                "foo": "${FOO}",
                "missing": "$MISSING",
                "multiple": "$A ${B} $C",
            }

        env = {
            "VAR": "hello world!",
            "FOO": 42,
            "A": "rock",
            "B": "paper",
            "C": "scissors",
        }

        subject.env_override = env

        config = subject.as_dict(session=session)
        assert config["var"] == env["VAR"]
        assert config["foo"] == str(env["FOO"])
        assert config["missing"] == None
        assert config["multiple"] == "rock paper scissors"

    def test_nested_keys(self, session, subject, project, tap):
        def set_config(path, value):
            subject.set(path, value, store=SettingValueStore.MELTANO_YML)

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
        set_config(["metadata.stream.replication-method"], None)

        yml = yml_config()
        assert "metadata" not in yml
        assert yml["metadata.stream.replication-key"] == "created_at"
        assert final_config()["metadata.stream.replication-key"] == "created_at"

        set_config(["metadata", "stream.replication-key"], "created_at")

        yml = yml_config()
        assert "metadata.stream.replication-key" not in yml
        assert yml["metadata"]["stream.replication-key"] == "created_at"
        assert final_config()["metadata.stream.replication-key"] == "created_at"

        set_config(["metadata", "stream.replication-key"], None)

        yml = yml_config()
        assert "metadata.stream.replication-key" not in yml
        assert "metadata" not in yml
        assert "metadata.stream.replication-key" not in final_config()

    def test_custom_setting(self, session, subject, tap, env_var):
        subject.set("custom_string", "from_yml", store=SettingValueStore.MELTANO_YML)
        subject.set("custom_bool", True, store=SettingValueStore.MELTANO_YML)

        assert subject.get_with_source("custom_string", session=session) == (
            "from_yml",
            SettingValueSource.MELTANO_YML,
        )
        assert subject.get_with_source("custom_bool", session=session) == (
            True,
            SettingValueSource.MELTANO_YML,
        )

        subject.env_override = {
            env_var(subject, "custom_string"): "from_env",
            env_var(subject, "custom_bool"): "off",
        }

        assert subject.get_with_source("custom_string", session=session) == (
            "from_env",
            SettingValueSource.ENV,
        )
        assert subject.get_with_source("custom_bool", session=session) == (
            False,
            SettingValueSource.ENV,
        )
