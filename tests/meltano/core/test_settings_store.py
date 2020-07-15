import pytest
from unittest import mock
from contextlib import contextmanager

from meltano.core.settings_service import SettingsService
from meltano.core.setting_definition import SettingDefinition
from meltano.core.settings_store import (
    SettingValueStore,
    StoreNotSupportedError,
    AutoStoreManager,
)

Store = SettingValueStore


class DummySettingsService(SettingsService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__meltano_yml_config = {}
        self.__definitions = [
            SettingDefinition("regular", value="from_default"),
            SettingDefinition("password", kind="password"),
            SettingDefinition("env_specific", env_specific=True),
        ]

    @property
    def _env_namespace(self):
        return "dummy"

    @property
    def _db_namespace(self):
        return "dummy"

    @property
    def _definitions(self):
        return self.__definitions

    @property
    def _meltano_yml_config(self):
        return self.__meltano_yml_config

    def _update_meltano_yml_config(self):
        pass


@pytest.fixture()
def dummy_settings_service(project):
    return DummySettingsService(project)


@pytest.fixture()
def subject(dummy_settings_service, session):
    manager = AutoStoreManager(dummy_settings_service, session=session)
    yield manager
    manager.reset()


@pytest.fixture()
def unsupported():
    @contextmanager
    def _unsupported(store):
        with mock.patch.object(
            store.manager, "ensure_supported", side_effect=StoreNotSupportedError
        ), mock.patch.object(
            store.manager, "set", side_effect=StoreNotSupportedError
        ), mock.patch.object(
            store.manager, "unset", side_effect=StoreNotSupportedError
        ), mock.patch.object(
            store.manager, "reset", side_effect=StoreNotSupportedError
        ):
            yield

    return _unsupported


@pytest.fixture()
def set_value_store(subject):
    def _set_value_store(value, store, name="regular"):
        subject.manager_for(store).set(name, [name], value)

    return _set_value_store


@pytest.fixture()
def assert_value_source(subject):
    def _assert_value_source(value, source, name="regular"):
        value, metadata = subject.get(name)
        assert value == value
        assert metadata["source"] == source

    return _assert_value_source


class TestAutoStoreManager:
    @pytest.mark.parametrize(
        "setting_name,preferred_store",
        [
            ("unknown", Store.MELTANO_YML),
            ("regular", Store.MELTANO_YML),
            ("password", Store.DOTENV),
            ("env_specific", Store.DOTENV),
        ],
    )
    def test_auto_store(self, setting_name, preferred_store, subject, unsupported):
        def auto_store(source):
            return subject.auto_store(setting_name, source)

        # Not writable
        assert auto_store(Store.CONFIG_OVERRIDE) == preferred_store
        assert auto_store(Store.ENV) == preferred_store
        assert auto_store(Store.DEFAULT) == preferred_store

        # Writable
        assert auto_store(Store.DOTENV) == Store.DOTENV
        assert auto_store(Store.MELTANO_YML) == Store.MELTANO_YML
        assert auto_store(Store.DB) == Store.DB

        # Fall back when writable store is not supported
        with unsupported(Store.DB):
            assert auto_store(Store.DB) == preferred_store

        with unsupported(Store.DOTENV):
            # Sensitive settings won't fall back on `meltano.yml`
            if preferred_store == Store.DOTENV:
                assert auto_store(Store.DOTENV) == Store.DB
            else:
                assert auto_store(Store.DOTENV) == Store.MELTANO_YML

        with unsupported(Store.MELTANO_YML):
            assert auto_store(Store.MELTANO_YML) == Store.DOTENV

        with unsupported(Store.DOTENV), unsupported(Store.MELTANO_YML):
            assert auto_store(Store.DOTENV) == Store.DB
            assert auto_store(Store.MELTANO_YML) == Store.DB

            with unsupported(Store.DB):
                assert auto_store(Store.DOTENV) == None
                assert auto_store(Store.MELTANO_YML) == None
                assert auto_store(Store.DB) == None

    def test_get(
        self,
        subject,
        dummy_settings_service,
        set_value_store,
        assert_value_source,
        monkeypatch,
    ):
        assert_value_source("from_default", Store.DEFAULT)

        set_value_store("from_db", Store.DB)
        assert_value_source("from_db", Store.DB)

        set_value_store("from_meltano_yml", Store.MELTANO_YML)
        assert_value_source("from_meltano_yml", Store.MELTANO_YML)

        set_value_store("from_dotenv", Store.DOTENV)
        assert_value_source("from_dotenv", Store.DOTENV)

        setting_def = subject.find_setting("regular")
        monkeypatch.setenv(dummy_settings_service.setting_env(setting_def), "from_env")
        assert_value_source("from_env", Store.ENV)

        monkeypatch.setitem(
            dummy_settings_service.config_override, "regular", "from_config_override"
        )
        assert_value_source("from_config_override", Store.CONFIG_OVERRIDE)

    def test_set(
        self, subject, unsupported, set_value_store, assert_value_source, monkeypatch
    ):
        def set_value(value):
            return subject.set("regular", ["regular"], value)

        # Returns silently when new value matches current value,
        # even if source is not writable
        assert_value_source("from_default", Store.DEFAULT)
        metadata = set_value("from_default")
        assert metadata["store"] == Store.DEFAULT
        assert_value_source("from_default", Store.DEFAULT)

        set_value_store("from_db", Store.DB)
        with mock.patch.object(
            Store.DB.manager, "set", side_effect=StoreNotSupportedError
        ):
            metadata = set_value("from_db")
            assert metadata["store"] == Store.DB
            assert_value_source("from_db", Store.DB)

        # Uses current store
        metadata = set_value("from_db_new")
        assert metadata["store"] == Store.DB
        assert_value_source("from_db_new", Store.DB)

        # Falls back on `meltano.yml` when current source is not writable
        with unsupported(Store.DB):
            metadata = set_value("from_meltano_yml")
            assert metadata["store"] == Store.MELTANO_YML
            assert_value_source("from_meltano_yml", Store.MELTANO_YML)

        # Unsets in all writable stores when new value matches default value
        metadata = set_value("from_default")
        assert metadata["store"] == Store.DEFAULT
        assert_value_source("from_default", Store.DEFAULT)

        # Stores in `meltano.yml` by default
        metadata = set_value("from_meltano_yml")
        assert metadata["store"] == Store.MELTANO_YML
        assert_value_source("from_meltano_yml", Store.MELTANO_YML)

        # Uses current store
        metadata = set_value("from_meltano_yml_new")
        assert metadata["store"] == Store.MELTANO_YML
        assert_value_source("from_meltano_yml_new", Store.MELTANO_YML)

        with unsupported(Store.MELTANO_YML):
            # Falls back on `.env` when current store is not supported
            metadata = set_value("from_dotenv")
            assert metadata["store"] == Store.DOTENV
            assert_value_source("from_dotenv", Store.DOTENV)

        # Uses current store
        metadata = set_value("from_dotenv_new")
        assert metadata["store"] == Store.DOTENV
        assert_value_source("from_dotenv_new", Store.DOTENV)

        # Falls back on `meltano.yml` when `.env` is not supported
        with unsupported(Store.DOTENV):
            metadata = set_value("from_meltano_yml")
            assert metadata["store"] == Store.MELTANO_YML

            # Even though `.env` can't be overwritten
            assert_value_source("from_dotenv_new", Store.DOTENV)

        # Falls back on system database when neither `.env` or `meltano.yml` are supported
        with unsupported(Store.DOTENV), unsupported(Store.MELTANO_YML):
            metadata = set_value("from_db")
            assert metadata["store"] == Store.DB

            # Even though `.env` can't be overwritten
            assert_value_source("from_dotenv_new", Store.DOTENV)

        # Fails if no stores are supported
        with unsupported(Store.DOTENV), unsupported(Store.MELTANO_YML), unsupported(
            Store.DB
        ):
            with pytest.raises(StoreNotSupportedError):
                set_value("nowhere")

            assert_value_source("from_dotenv_new", Store.DOTENV)

    def test_unset(self, subject, unsupported, set_value_store, assert_value_source):
        set_value_store("from_dotenv", Store.DOTENV, name="password")

        set_value_store("from_dotenv", Store.DOTENV)
        set_value_store("from_meltano_yml", Store.MELTANO_YML)
        set_value_store("from_db", Store.DB)

        metadata = subject.unset("regular", ["regular"])
        assert metadata["store"] == Store.DB
        assert_value_source("from_default", Store.DEFAULT)

        assert_value_source("from_dotenv", Store.DOTENV, name="password")

        # Fails when store is not supported
        with unsupported(Store.DOTENV):
            with pytest.raises(StoreNotSupportedError):
                subject.unset("password", ["password"])

            assert_value_source("from_dotenv", Store.DOTENV, name="password")

    def test_reset(self, subject, unsupported, set_value_store, assert_value_source):
        set_value_store("from_db", Store.DB)
        set_value_store("from_meltano_yml", Store.MELTANO_YML, name="unknown")
        set_value_store("from_dotenv", Store.DOTENV, name="password")
        set_value_store("from_db", Store.DB, name="env_specific")

        subject.reset()

        assert_value_source("from_default", Store.DEFAULT)
        assert_value_source(None, Store.DEFAULT, name="unknown")
        assert_value_source(None, Store.DEFAULT, name="password")
        assert_value_source(None, Store.DEFAULT, name="env_specific")

        # Fails silently when store is not supported
        set_value_store("from_dotenv", Store.DOTENV, name="password")
        with unsupported(Store.DOTENV):
            subject.reset()

            assert_value_source("from_dotenv", Store.DOTENV, name="password")
