from __future__ import annotations

from contextlib import contextmanager

import mock
import pytest

from meltano.core.environment import Environment
from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.setting_definition import SettingDefinition, SettingKind
from meltano.core.settings_service import SettingsService
from meltano.core.settings_store import (
    AutoStoreManager,
    InheritedStoreManager,
    MeltanoEnvStoreManager,
    MeltanoYmlStoreManager,
    SettingsStoreManager,
    SettingValueStore,
    StoreNotSupportedError,
)

Store = SettingValueStore


class DummySettingsService(SettingsService):
    """Dummy SettingsService for testing."""

    def __init__(self, *args, **kwargs):
        """Instantiate new DummySettingsService instance.

        Args:
            args: Positional arguments to pass to the superclass.
            kwargs: Keyword arguments to pass to the superclass.
        """
        super().__init__(*args, **kwargs)

        self.__meltano_yml_config = {}
        self._meltano_environment_config = {}
        self.__definitions = [
            SettingDefinition("regular", aliases=["basic"], value="from_default"),
            SettingDefinition("password", kind=SettingKind.PASSWORD),
            SettingDefinition("env_specific", env_specific=True),
        ]
        self._inherited_settings = None

    @property
    def label(self):
        return "Dummy"

    @property
    def project_settings_service(self):
        return ProjectSettingsService(Project.find())

    @property
    def docs_url(self):
        return "https://docs.meltano.com/"

    @property
    def env_prefixes(self):
        return ["dummy"]

    @property
    def db_namespace(self):
        return "dummy"

    @property
    def setting_definitions(self):
        return self.__definitions

    @property
    def meltano_yml_config(self):
        return self.__meltano_yml_config

    def update_meltano_yml_config(self, config):
        self.__meltano_yml_config = config

    def update_meltano_environment_config(self, config):
        self._meltano_environment_config = config

    @property
    def inherited_settings_service(self):
        return self._inherited_settings

    def process_config(self, config):
        return config

    @property
    def environment_config(self) -> dict:
        return self._meltano_environment_config


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
    def environment(self):
        return Environment("testing", {})

    @pytest.fixture()
    def assert_value_source(self, subject):
        def _assert_value_source(value, source, name="regular"):
            new_value, metadata = subject.get(
                name, setting_def=subject.find_setting(name)
            )
            assert new_value == value
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
        self,
        setting_name,
        preferred_store,
        subject,
        project,
        unsupported,
        environment,
        monkeypatch,
    ):
        assert subject.auto_store(setting_name) == preferred_store

        # Meltano environment is selected only when there's an active environment
        with monkeypatch.context() as mpc:
            mpc.setattr(project, "active_environment", environment)
            if preferred_store == Store.MELTANO_YML:
                assert subject.auto_store(setting_name) == Store.MELTANO_ENV

        with unsupported(Store.DOTENV):
            # Sensitive settings won't fall back on `meltano.yml`
            if setting_name == "password":
                assert subject.auto_store(setting_name) == Store.DB
            else:
                assert subject.auto_store(setting_name) == Store.MELTANO_YML
                with monkeypatch.context() as mpc:
                    mpc.setattr(project, "active_environment", environment)
                    assert subject.auto_store(setting_name) == Store.MELTANO_ENV

        with unsupported(Store.MELTANO_YML):
            # fall back on dotenv
            if preferred_store == Store.MELTANO_YML:
                assert subject.auto_store(setting_name) == Store.DOTENV
                with monkeypatch.context() as mpc:
                    mpc.setattr(project, "active_environment", environment)
                    assert subject.auto_store(setting_name) == Store.DOTENV

        with unsupported(Store.DOTENV), unsupported(Store.MELTANO_YML):
            assert subject.auto_store(setting_name) == Store.DB
            with monkeypatch.context() as mpc:
                mpc.setattr(project, "active_environment", environment)
                assert subject.auto_store(setting_name) == Store.DB

            with unsupported(Store.DB):
                assert subject.auto_store(setting_name) is None

        monkeypatch.setattr(project, "readonly", True)

        assert subject.auto_store(setting_name) == Store.DB

    def test_get(  # noqa: WPS213
        self,
        subject,
        project,
        dummy_settings_service,
        set_value_store,
        assert_value_source,
        monkeypatch,
        environment,
    ):
        value, metadata = subject.get("regular")
        assert value == "from_default"
        assert metadata["source"] == Store.DEFAULT
        assert metadata["auto_store"] == Store.MELTANO_YML
        assert metadata["overwritable"] is True

        with monkeypatch.context() as mpc:
            mpc.setattr(project, "active_environment", environment)
            value, metadata = subject.get("regular")
            assert value == "from_default"
            assert metadata["source"] == Store.DEFAULT
            assert metadata["auto_store"] == Store.MELTANO_ENV
            assert metadata["overwritable"] is True

        set_value_store("from_db", Store.DB)
        value, metadata = subject.get("regular")
        assert value == "from_db"
        assert metadata["source"] == Store.DB
        assert metadata["auto_store"] == Store.MELTANO_YML
        assert metadata["overwritable"] is True

        set_value_store("from_meltano_yml", Store.MELTANO_YML)
        value, metadata = subject.get("regular")
        assert value == "from_meltano_yml"
        assert metadata["source"] == Store.MELTANO_YML
        assert metadata["auto_store"] == Store.MELTANO_YML
        assert metadata["overwritable"] is True

        with monkeypatch.context() as mpc:
            mpc.setattr(project, "active_environment", environment)
            set_value_store("from_meltano_env", Store.MELTANO_ENV)
            value, metadata = subject.get("regular")
            assert value == "from_meltano_env"
            assert metadata["source"] == Store.MELTANO_ENV
            assert metadata["auto_store"] == Store.MELTANO_ENV
            assert metadata["overwritable"] is True

        set_value_store("from_dotenv", Store.DOTENV)
        value, metadata = subject.get("regular")
        assert value == "from_dotenv"
        assert metadata["source"] == Store.DOTENV
        assert metadata["auto_store"] == Store.MELTANO_YML
        assert metadata["overwritable"] is False

        setting_def = subject.find_setting("regular")
        monkeypatch.setenv(dummy_settings_service.setting_env(setting_def), "from_env")
        value, metadata = subject.get("regular")
        assert value == "from_env"
        assert metadata["source"] == Store.ENV
        assert metadata["auto_store"] == Store.MELTANO_YML
        assert metadata["overwritable"] is False

        monkeypatch.setitem(
            dummy_settings_service.config_override, "regular", "from_config_override"
        )
        value, metadata = subject.get("regular")
        assert value == "from_config_override"
        assert metadata["source"] == Store.CONFIG_OVERRIDE
        assert metadata["auto_store"] == Store.MELTANO_YML
        assert metadata["overwritable"] is False

        with monkeypatch.context() as mpc:
            mpc.setattr(project, "active_environment", environment)
            value, metadata = subject.get("regular")
            assert value == "from_config_override"
            assert metadata["source"] == Store.CONFIG_OVERRIDE
            assert metadata["auto_store"] == Store.MELTANO_ENV
            assert metadata["overwritable"] is False

        monkeypatch.setattr(project, "readonly", True)
        value, metadata = subject.get("regular")
        assert value == "from_config_override"
        assert metadata["source"] == Store.CONFIG_OVERRIDE
        assert metadata["auto_store"] == Store.DB
        assert metadata["overwritable"] is False

    def test_set(
        self,
        subject: SettingsStoreManager,
        project,
        unsupported,
        set_value_store,
        assert_value_source,
        monkeypatch,
        environment,
    ):
        def set_value(value):
            return subject.set("regular", ["regular"], value)

        # Allow setting to a default value
        assert_value_source("from_default", Store.DEFAULT)
        metadata = set_value("from_default")
        assert metadata["store"] == Store.MELTANO_YML
        assert_value_source("from_default", Store.MELTANO_YML)

        # Falls back on `meltano.yml` when current source is not writable
        with unsupported(Store.DB):
            metadata = set_value("from_meltano_yml")
            assert metadata["store"] == Store.MELTANO_YML
            assert_value_source("from_meltano_yml", Store.MELTANO_YML)

        # Stores in Meltano Environment if active
        with monkeypatch.context() as mpc:
            mpc.setattr(project, "active_environment", environment)
            metadata = set_value("from_meltano_env")
            assert metadata["store"] == Store.MELTANO_ENV
            assert_value_source("from_meltano_env", Store.MELTANO_ENV)

        # Stores in `meltano.yml` by default
        metadata = set_value("from_meltano_yml")
        assert metadata["store"] == Store.MELTANO_YML
        assert_value_source("from_meltano_yml", Store.MELTANO_YML)

        with unsupported(Store.MELTANO_YML):
            # Falls back on `.env` when current store is not supported
            metadata = set_value("from_dotenv")
            assert metadata["store"] == Store.DOTENV
            assert_value_source("from_dotenv", Store.DOTENV)

        # Falls back on `meltano.yml` when `.env` is not supported
        with unsupported(Store.DOTENV):
            metadata = set_value("from_meltano_yml")
            assert metadata["store"] == Store.MELTANO_YML
            # Even though `.env` can't be overwritten
            assert_value_source("from_dotenv", Store.DOTENV)

        # Falls back on system database when neither `.env` or `meltano.yml` are supported
        with unsupported(Store.DOTENV), unsupported(Store.MELTANO_YML):
            metadata = set_value("from_db")
            assert metadata["store"] == Store.DB
            # Even though `.env` can't be overwritten
            assert_value_source("from_dotenv", Store.DOTENV)

        # Fails if no stores are supported
        with unsupported(Store.DOTENV), unsupported(Store.MELTANO_YML), unsupported(
            Store.DB
        ):
            with pytest.raises(StoreNotSupportedError):
                set_value("nowhere")

            assert_value_source("from_dotenv", Store.DOTENV)

        # Falls back on system database when project is readonly
        monkeypatch.setattr(project, "readonly", True)
        metadata = set_value("from_db")
        assert metadata["store"] == Store.DB

        # Even though `.env` can't be overwritten
        assert_value_source("from_dotenv", Store.DOTENV)

    def test_unset(  # noqa: WPS213
        self,
        subject,
        project,
        unsupported,
        set_value_store,
        assert_value_source,
        monkeypatch,
        environment,
    ):
        set_value_store("from_dotenv", Store.DOTENV, name="password")

        set_value_store("from_dotenv", Store.DOTENV)
        set_value_store("from_meltano_yml", Store.MELTANO_YML)
        set_value_store("from_db", Store.DB)

        with monkeypatch.context() as mpc:
            mpc.setattr(project, "active_environment", environment)
            set_value_store("from_meltano_environment", Store.MELTANO_ENV)

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

        with monkeypatch.context() as mpc:
            mpc.setattr(project, "active_environment", environment)
            subject.manager_for(Store.MELTANO_ENV).set(
                "custom_in_env", ["custom_in_env"], "from_meltano_environment"
            )
            assert_value_source(
                "from_meltano_environment", Store.MELTANO_ENV, name="custom_in_env"
            )

        subject.unset("custom_in_env", ["custom_in_env"])
        assert_value_source(None, Store.DEFAULT, name="custom_in_env")

    def test_reset(  # noqa: WPS213
        self,
        subject,
        unsupported,
        set_value_store,
        assert_value_source,
        project,
        environment,
        monkeypatch,
    ):
        set_value_store("from_db", Store.DB)
        set_value_store("from_meltano_yml", Store.MELTANO_YML, name="unknown")
        set_value_store("from_dotenv", Store.DOTENV, name="password")
        set_value_store("from_db", Store.DB, name="env_specific")
        with monkeypatch.context() as mpc:
            mpc.setattr(project, "active_environment", environment)
            set_value_store(
                "from_meltano_environment", Store.MELTANO_ENV, name="dataops"
            )

        subject.reset()

        assert_value_source("from_default", Store.DEFAULT)
        assert_value_source(None, Store.DEFAULT, name="unknown")
        assert_value_source(None, Store.DEFAULT, name="password")
        assert_value_source(None, Store.DEFAULT, name="env_specific")
        assert_value_source(None, Store.DEFAULT, name="dataops")
        with monkeypatch.context() as mpc:
            mpc.setattr(project, "active_environment", environment)
            assert_value_source(
                "from_meltano_environment", Store.MELTANO_ENV, name="dataops"
            )

        # Fails silently when store is not supported
        set_value_store("from_dotenv", Store.DOTENV, name="password")
        with unsupported(Store.DOTENV):
            subject.reset()

            assert_value_source("from_dotenv", Store.DOTENV, name="password")

        with monkeypatch.context() as mpc:
            mpc.setattr(project, "active_environment", environment)
            set_value_store(
                "from_meltano_environment", Store.MELTANO_ENV, name="dataops"
            )
            assert_value_source(
                "from_meltano_environment", Store.MELTANO_ENV, name="dataops"
            )

        # Resetting without an active environment has no effect on config 'dataops'
        subject.reset()
        with monkeypatch.context() as mpc:
            mpc.setattr(project, "active_environment", environment)
            assert_value_source(
                "from_meltano_environment", Store.MELTANO_ENV, name="dataops"
            )

        # Resetting with an active environment works fine :)
        with monkeypatch.context() as mpc:
            mpc.setattr(project, "active_environment", environment)
            subject.reset()
            assert_value_source(None, Store.DEFAULT, name="dataops")


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

        assert get() == ("alias_value", {"expandable": True, "key": "basic"})

        subject.flat_config.pop("basic")
        subject.flat_config["regular"] = "value"

        assert get() == ("value", {"expandable": True, "key": "regular"})

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


class TestMeltanoEnvironmentStoreManager(TestMeltanoYmlStoreManager):
    @pytest.fixture()
    def subject(self, dummy_settings_service, project):
        project.active_environment = Environment("testing", {})
        manager = MeltanoEnvStoreManager(dummy_settings_service)
        yield manager
        project.active_environment = None
        manager.reset()


class TestInheritedStoreManager:
    @pytest.fixture()
    def subject(self, dummy_settings_service):
        return InheritedStoreManager(dummy_settings_service)

    def test_get(self, subject, project):
        def get(key="regular"):
            return subject.get(
                key, setting_def=subject.settings_service.find_setting(key)
            )

        with pytest.raises(StoreNotSupportedError):
            get()

        inherited_settings = DummySettingsService(project)
        subject.settings_service._inherited_settings = inherited_settings

        # Default values are not inherited
        assert inherited_settings.get_with_source("regular") == (
            "from_default",
            Store.DEFAULT,
        )
        assert get() == (None, {})

        # Non-default values are inherited
        inherited_settings.set("regular", "$YML_VALUE", store=Store.MELTANO_YML)
        value, metadata = get()

        # Env vars are not expanded in values
        assert value == "$YML_VALUE"
        assert metadata["inherited_source"] is Store.MELTANO_YML
        # Env var expandability is inherited
        assert metadata["expandable"]

        inherited_settings.set("regular", "$DOTENV_VALUE", store=Store.DOTENV)
        value, metadata = get()
        assert value == "$DOTENV_VALUE"
        assert metadata["inherited_source"] is Store.DOTENV
        # Lack of env var expandability is inherited
        assert not metadata["expandable"]
