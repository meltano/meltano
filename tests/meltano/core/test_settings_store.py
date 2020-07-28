import pytest
from unittest import mock
from contextlib import contextmanager

from meltano.core.settings_service import SettingsService
from meltano.core.setting_definition import SettingDefinition
from meltano.core.settings_store import (
    SettingValueStore,
    StoreNotSupportedError,
    AutoStoreManager,
    MeltanoYmlStoreManager,
)

Store = SettingValueStore


class DummySettingsService(SettingsService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__meltano_yml_config = {}
        self.__definitions = [
            SettingDefinition("regular", aliases=["basic"], value="from_default"),
            SettingDefinition("password", kind="password"),
            SettingDefinition("env_specific", env_specific=True),
        ]

    @property
    def label(self):
        return "Dummy"

    @property
    def docs_url(self):
        return "https://meltano.com/docs/"

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

    def _update_meltano_yml_config(self, config):
        self.__meltano_yml_config = config

    def _process_config(self, config):
        return config


@pytest.fixture()
def dummy_settings_service(project):
    return DummySettingsService(project)


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


class TestAutoStoreManager:
    @pytest.fixture()
    def subject(self, dummy_settings_service, session):
        manager = AutoStoreManager(dummy_settings_service, session=session, cache=False)
        yield manager
        manager.reset()

    @pytest.fixture()
    def set_value_store(self, subject):
        def _set_value_store(value, store, name="regular"):
            subject.manager_for(store).set(
                name, [name], value, setting_def=subject.find_setting(name)
            )

        return _set_value_store

    @pytest.fixture()
    def assert_value_source(self, subject):
        def _assert_value_source(value, source, name="regular"):
            value, metadata = subject.get(name, setting_def=subject.find_setting(name))
            assert value == value
            assert metadata["source"] == source

        return _assert_value_source

    @pytest.mark.parametrize(
        "setting_name,preferred_store",
        [
            ("unknown", Store.MELTANO_YML),
            ("regular", Store.MELTANO_YML),
            ("password", Store.DOTENV),
            ("env_specific", Store.DOTENV),
        ],
    )
    def test_auto_store(
        self, setting_name, preferred_store, subject, project, unsupported, monkeypatch
    ):
        def auto_store(source):
            return subject.auto_store(setting_name, source)

        # Not writable
        assert auto_store(Store.CONFIG_OVERRIDE) == preferred_store
        assert auto_store(Store.ENV) == Store.DOTENV
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

        monkeypatch.setattr(project, "readonly", True)

        assert auto_store(Store.CONFIG_OVERRIDE) == Store.DB
        assert auto_store(Store.ENV) == Store.DB
        assert auto_store(Store.DOTENV) == Store.DB
        assert auto_store(Store.MELTANO_YML) == Store.DB
        assert auto_store(Store.DB) == Store.DB
        assert auto_store(Store.DEFAULT) == Store.DB

    def test_get(
        self,
        subject,
        project,
        dummy_settings_service,
        set_value_store,
        assert_value_source,
        monkeypatch,
    ):
        value, metadata = subject.get("regular")
        assert value == "from_default"
        assert metadata["source"] == Store.DEFAULT
        assert metadata["auto_store"] == Store.MELTANO_YML
        assert metadata["overwritable"] == True

        set_value_store("from_db", Store.DB)
        value, metadata = subject.get("regular")
        assert value == "from_db"
        assert metadata["source"] == Store.DB
        assert metadata["auto_store"] == Store.DB
        assert metadata["overwritable"] == True

        set_value_store("from_meltano_yml", Store.MELTANO_YML)
        value, metadata = subject.get("regular")
        assert value == "from_meltano_yml"
        assert metadata["source"] == Store.MELTANO_YML
        assert metadata["auto_store"] == Store.MELTANO_YML
        assert metadata["overwritable"] == True

        set_value_store("from_dotenv", Store.DOTENV)
        value, metadata = subject.get("regular")
        assert value == "from_dotenv"
        assert metadata["source"] == Store.DOTENV
        assert metadata["auto_store"] == Store.DOTENV
        assert metadata["overwritable"] == True

        setting_def = subject.find_setting("regular")
        monkeypatch.setenv(dummy_settings_service.setting_env(setting_def), "from_env")
        value, metadata = subject.get("regular")
        assert value == "from_env"
        assert metadata["source"] == Store.ENV
        assert metadata["auto_store"] == Store.DOTENV
        assert metadata["overwritable"] == False

        monkeypatch.setitem(
            dummy_settings_service.config_override, "regular", "from_config_override"
        )
        value, metadata = subject.get("regular")
        assert value == "from_config_override"
        assert metadata["source"] == Store.CONFIG_OVERRIDE
        assert metadata["auto_store"] == Store.MELTANO_YML
        assert metadata["overwritable"] == False

        monkeypatch.setattr(project, "readonly", True)
        value, metadata = subject.get("regular")
        assert value == "from_config_override"
        assert metadata["source"] == Store.CONFIG_OVERRIDE
        assert metadata["auto_store"] == Store.DB
        assert metadata["overwritable"] == False

    def test_set(
        self,
        subject,
        project,
        unsupported,
        set_value_store,
        assert_value_source,
        monkeypatch,
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

        # Falls back on system database when project is readonly
        monkeypatch.setattr(project, "readonly", True)
        metadata = set_value("from_db")
        assert metadata["store"] == Store.DB

        # Even though `.env` can't be overwritten
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

        # Unsets even when there is technically no setting with that exact full name
        subject.manager_for(Store.MELTANO_YML).set(
            "custom.nested", ["custom", "nested"], "from_meltano_yml"
        )
        assert_value_source(None, Store.DEFAULT, name="custom")
        assert_value_source("from_meltano_yml", Store.MELTANO_YML, name="custom.nested")

        subject.unset("custom", ["custom"])
        assert_value_source(None, Store.DEFAULT, name="custom")
        assert_value_source(None, Store.DEFAULT, name="custom.nested")

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


class TestMeltanoYmlStoreManager:
    @pytest.fixture()
    def subject(self, dummy_settings_service):
        manager = MeltanoYmlStoreManager(dummy_settings_service)
        yield manager
        manager.reset()

    def test_get(self, subject):
        def get():
            return subject.get(
                "regular", setting_def=subject.settings_service.find_setting("regular")
            )

        assert get() == (None, {})

        subject.flat_config["basic"] = "alias_value"

        assert get() == ("alias_value", {"key": "basic"})

        subject.flat_config["regular"] = "value"

        assert get() == ("value", {"key": "regular"})

    def test_set(self, subject):
        def set_value(key, value):
            return subject.set(
                key,
                [key],
                value,
                setting_def=subject.settings_service.find_setting(key),
            )

        subject.flat_config["basic"] = "alias_value"

        set_value("basic", "new_alias_value")

        assert "regular" not in subject.flat_config
        assert subject.flat_config["basic"] == "new_alias_value"

        set_value("regular", "new_value")

        assert "basic" not in subject.flat_config
        assert subject.flat_config["regular"] == "new_value"

    def test_unset(self, subject):
        def unset_value(key):
            return subject.unset(
                key, [key], setting_def=subject.settings_service.find_setting(key)
            )

        def set_values():
            subject.flat_config["regular"] = "value"
            subject.flat_config["basic"] = "alias_value"

        set_values()
        unset_value("regular")

        assert "regular" not in subject.flat_config
        assert "basic" not in subject.flat_config

        set_values()
        unset_value("basic")

        assert "regular" not in subject.flat_config
        assert "basic" not in subject.flat_config
