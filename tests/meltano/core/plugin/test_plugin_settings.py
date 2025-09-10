from __future__ import annotations

import platform
import re
import typing as t
from datetime import datetime, timezone

import dotenv
import pytest

from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.project_plugins_service import PluginAlreadyAddedException
from meltano.core.setting import Setting
from meltano.core.settings_service import (
    FEATURE_FLAG_PREFIX,
    REDACTED_VALUE,
    FeatureFlags,
    SettingValueStore,
)
from meltano.core.settings_store import (
    ConflictingSettingValueException,
    MultipleEnvVarsSetException,
)
from meltano.core.utils import EnvironmentVariableNotSetError

if t.TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from sqlalchemy.orm import Session

    from meltano.core.environment import Environment
    from meltano.core.plugin.settings_service import PluginSettingsService
    from meltano.core.project import Project

    PluginSettingsServiceFactory: t.TypeAlias = Callable[
        [ProjectPlugin],
        PluginSettingsService,
    ]


@pytest.mark.order(0)
def test_create(session) -> None:
    setting = Setting(
        name="api_key.test.test",
        namespace="gitlab",
        value="C4F3C4F3",
        enabled=True,
    )

    session.add(setting)
    session.commit()

    fetched = session.query(Setting).first()
    assert setting == fetched


@pytest.fixture(scope="class")
def env_var():
    def _wrapper(plugin_settings_service, setting_name):
        setting_def = plugin_settings_service.find_setting(setting_name)
        return plugin_settings_service.setting_env(setting_def)

    return _wrapper


@pytest.fixture(scope="class")
def custom_tap(project: Project):
    expected = {"test": "custom", "start_date": None, "secure": None}
    tap = ProjectPlugin(
        PluginType.EXTRACTORS,
        name="tap-custom",
        namespace="tap_custom",
        config=expected,
    )
    try:
        return project.plugins.add_to_file(tap)
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture
def subject(tap, plugin_settings_service_factory) -> PluginSettingsService:
    return plugin_settings_service_factory(tap)


@pytest.fixture
def environment(project: Project) -> Generator[Environment, None, None]:
    project.activate_environment("dev")
    try:
        yield project.environment
    finally:
        project.deactivate_environment()


class TestPluginSettingsService:
    def test_get_with_source(
        self,
        session,
        tap,
        inherited_tap,
        env_var,
        monkeypatch,
        plugin_settings_service_factory,
    ) -> None:
        subject = plugin_settings_service_factory(inherited_tap)

        # returns the default value when unset
        assert subject.get_with_source("test", session=session) == (
            "mock",
            SettingValueStore.DEFAULT,
        )

        # returns the inherited value when set
        parent_subject = plugin_settings_service_factory(tap)
        monkeypatch.setenv(env_var(parent_subject, "test"), "INHERITED")

        assert subject.get_with_source("test", session=session) == (
            "INHERITED",
            SettingValueStore.INHERITED,
        )

        # overriden by an Setting db value when set
        subject.set(
            "test",
            "THIS_IS_FROM_DB",
            store=SettingValueStore.DB,
            session=session,
        )

        assert subject.get_with_source("test", session=session) == (
            "THIS_IS_FROM_DB",
            SettingValueStore.DB,
        )

        # overriden via the `meltano.yml` configuration
        test_value = 42
        subject.set(
            "test",
            test_value,
            store=SettingValueStore.MELTANO_YML,
            session=session,
        )

        assert subject.get_with_source("test", session=session) == (
            test_value,
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

    def test_get_with_source_casting(
        self,
        session,
        subject,
        env_var,
        monkeypatch,
    ) -> None:
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

        # Preferred env var
        monkeypatch.setenv(env_var(subject, "boolean"), "0")

        assert subject.get_with_source("boolean", session=session) == (
            False,
            SettingValueStore.ENV,
        )

    def test_get_expandable_inherited(
        self,
        session: Session,
        monkeypatch: pytest.MonkeyPatch,
        plugin_settings_service_factory: PluginSettingsServiceFactory,
        inherited_tap,
    ) -> None:
        """Casting is disabled for expandable strings."""
        monkeypatch.setenv("PORT", "4444")
        service = plugin_settings_service_factory(inherited_tap)
        parent = service.inherited_settings_service
        parent.set(
            "port",
            "5555",
            store=SettingValueStore.MELTANO_YML,
            cast_value=False,
        )
        value, metadata = service.get_with_metadata("port", session=session)
        assert value == 5555
        assert metadata["source"] is SettingValueStore.INHERITED
        assert metadata["uncast_value"] == "5555"
        assert "unexpanded_value" not in metadata
        assert not metadata["expandable"]

        parent.set(
            "port",
            "$PORT",
            store=SettingValueStore.MELTANO_YML,
            cast_value=False,
        )
        value, metadata = parent.get_with_metadata("port", session=session)
        assert value == 4444
        assert metadata["source"] is SettingValueStore.MELTANO_YML
        assert metadata["uncast_value"] == "4444"
        assert metadata["expanded"]
        assert metadata["unexpanded_value"] == "$PORT"
        assert not metadata["expandable"]

        value, metadata = service.get_with_metadata("port", session=session)
        assert value == 4444
        assert metadata["source"] is SettingValueStore.INHERITED
        assert metadata["inherited_source"] is SettingValueStore.MELTANO_YML
        assert metadata["uncast_value"] == "4444"
        assert metadata["expanded"]
        assert metadata["unexpanded_value"] == "$PORT"
        assert not metadata["expandable"]

    def test_definitions(self, subject) -> None:
        subject.show_hidden = False
        subject._setting_defs = None

        setting_defs_by_name = {sdef.name: sdef for sdef in subject.definitions()}

        # Regular settings
        assert "test" in setting_defs_by_name
        assert "start_date" in setting_defs_by_name

        # Expect hidden
        assert "secret" not in setting_defs_by_name

    @pytest.mark.order(1)
    @pytest.mark.usefixtures("tap")
    def test_as_dict(self, subject, session) -> None:
        expected = {"test": "mock", "start_date": None, "secure": None}
        full_config = subject.as_dict(session=session)
        redacted_config = subject.as_dict(redacted=True, session=session)

        for key, value in expected.items():
            assert full_config.get(key) == value
            assert redacted_config.get(key) == value

    @pytest.mark.filterwarnings("ignore:Unknown setting:RuntimeWarning")
    def test_environment_only_config(
        self,
        environment: Environment,
        subject: PluginSettingsService,
        project: Project,
    ) -> None:
        subject.set("test_environment", "THIS_IS_FROM_ENVIRONMENT")
        by_name = {sdef.name: sdef for sdef in subject.definitions()}

        assert "test_environment" in by_name
        assert not by_name["test"].is_custom
        assert by_name["test_environment"].is_custom

        with project.meltano_update() as meltano:
            plugin = meltano.plugins.extractors[0]
            assert "test_environment" not in plugin.config

            dev_environment = meltano.environments[0]
            env_plugin = dev_environment.config.plugins[PluginType.EXTRACTORS][0]
            assert dev_environment == environment
            assert env_plugin.config["test_environment"] == "THIS_IS_FROM_ENVIRONMENT"

    @pytest.mark.usefixtures("tap")
    def test_as_dict_process(self, subject: PluginSettingsService) -> None:
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
        assert config["auth"]["password"] == "nested_password"  # noqa: S105
        assert "auth.username" not in config
        assert "auth.password" not in config

    @pytest.mark.usefixtures("project")
    def test_as_dict_custom(
        self,
        session,
        custom_tap,
        plugin_settings_service_factory,
    ) -> None:
        subject = plugin_settings_service_factory(custom_tap)
        assert subject.as_dict(extras=False, session=session) == custom_tap.config

    @pytest.mark.usefixtures("tap")
    def test_as_dict_redacted(self, subject, session) -> None:
        store = SettingValueStore.DB

        # ensure values are redacted when they are set
        subject.set("secure", "thisisatest", store=store, session=session)

        config = subject.as_dict(redacted=True, session=session)
        assert config["secure"] == REDACTED_VALUE

        config = subject.as_dict(redacted=True, session=session, redacted_value="*****")
        assert config["secure"] == "*****"

        # although setting the REDACTED_VALUE does nothing
        subject.set("secure", REDACTED_VALUE, store=store, session=session)
        config = subject.as_dict(session=session)
        assert config["secure"] == "thisisatest"

    @pytest.mark.usefixtures("tap")
    def test_as_env(self, subject, session, env_var) -> None:
        subject.set("boolean", value=True, store=SettingValueStore.DOTENV)
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

        # Generic env vars are present
        assert config["MELTANO_EXTRACT_TEST"] == "mock"
        assert config["MELTANO_EXTRACT_LIST"] == '[1, 2, 3, "4"]'
        assert config["MELTANO_EXTRACT_OBJECT"] == '{"1": {"2": 3}}'
        assert config["MELTANO_EXTRACT_BOOLEAN"] == "true"

    @pytest.mark.usefixtures("project")
    def test_as_env_custom(
        self,
        session,
        custom_tap,
        env_var,
        plugin_settings_service_factory,
    ) -> None:
        subject = plugin_settings_service_factory(custom_tap)
        config = subject.as_env(session=session)
        for key, value in custom_tap.config.items():
            assert config.get(env_var(subject, key)) == value

    @pytest.mark.order(4)
    @pytest.mark.usefixtures("env_var")
    def test_namespace_as_env_prefix(
        self,
        project: Project,
        session,
        target: ProjectPlugin,
        plugin_settings_service_factory,
    ) -> None:
        subject = plugin_settings_service_factory(target)

        def assert_env_value(value, env_var) -> None:
            read_value, metadata = subject.get_with_metadata("schema")
            assert value == read_value
            assert metadata["env_var"] == env_var

        assert subject.get("schema") is None

        subject.set("schema", "default", store=SettingValueStore.DOTENV)
        _value, _metadata = subject.get_with_metadata("schema")

        # Env is the default
        assert_env_value("default", "TARGET_MOCK_SCHEMA")

        subject.unset("schema")

        # Namespace prefix
        dotenv.set_key(project.dotenv, "MOCK_SCHEMA", "namespace_prefix")
        assert_env_value("namespace_prefix", "MOCK_SCHEMA")

        # Name prefix
        dotenv.unset_key(project.dotenv, "MOCK_SCHEMA")
        dotenv.set_key(project.dotenv, "TARGET_MOCK_SCHEMA", "name_prefix")
        project.refresh()
        assert_env_value("name_prefix", "TARGET_MOCK_SCHEMA")

        config = subject.as_env(session=session)
        subject.reset(store=SettingValueStore.DOTENV)

        assert (
            config["MELTANO_LOAD_SCHEMA"] == "name_prefix"
        )  # Generic prefix, read-only

    def test_setting_env_vars(
        self,
        tap,
        inherited_tap,
        alternative_target,
        plugin_settings_service_factory,
    ) -> None:
        def env_vars(service, setting_name, **kwargs):
            return [
                setting.definition
                for setting in service.setting_env_vars(
                    service.find_setting(setting_name),
                    **kwargs,
                )
            ]

        # Shadowing base plugin
        service = plugin_settings_service_factory(tap)
        # For reading setting values from environment
        assert env_vars(service, "boolean") == [
            "TAP_MOCK_BOOLEAN",  # Name and namespace prefix
        ]
        # For writing values into the execution environment
        assert env_vars(service, "boolean", for_writing=True) == [
            "TAP_MOCK_BOOLEAN",  # Name and namespace prefix
            "MELTANO_EXTRACT_BOOLEAN",  # Generic prefix
        ]

        # Inheriting from base plugin
        service = plugin_settings_service_factory(alternative_target)
        # For reading setting values from environment
        assert env_vars(service, "schema") == [
            "TARGET_MOCK_ALTERNATIVE_SCHEMA",  # Name and namespace prefix
        ]
        # For writing values into the execution environment
        assert env_vars(service, "schema", for_writing=True) == [
            "MOCKED_SCHEMA",  # Custom `env`
            "TARGET_MOCK_ALTERNATIVE_SCHEMA",  # Name and namespace prefix
            "TARGET_MOCK_SCHEMA",  # Parent name prefix
            "MOCK_SCHEMA",  # Parent namespace prefix
            "MELTANO_LOAD_SCHEMA",  # Generic prefix
        ]

        # Inheriting from project plugin
        service = plugin_settings_service_factory(inherited_tap)
        # For reading setting values from environment
        assert env_vars(service, "boolean") == [
            "TAP_MOCK_INHERITED_BOOLEAN",  # Name and namespace prefix
        ]
        # For writing values into the execution environment
        assert env_vars(service, "boolean", for_writing=True) == [
            "TAP_MOCK_INHERITED_BOOLEAN",  # Name and namespace prefix
            "TAP_MOCK_BOOLEAN",  # Parent name and namespace prefix
            "MELTANO_EXTRACT_BOOLEAN",  # Generic prefix
        ]

    @pytest.mark.usefixtures("tap")
    @pytest.mark.filterwarnings("ignore:Unknown setting:RuntimeWarning")
    def test_store_db(self, session, subject) -> None:
        store = SettingValueStore.DB

        subject.set("test_a", "THIS_IS_FROM_DB", store=store, session=session)
        subject.set("test_b", "THIS_IS_FROM_DB", store=store, session=session)

        assert session.query(Setting).count() == 2

        subject.unset("test_a", store=store, session=session)

        assert session.query(Setting).count() == 1

        subject.reset(store=store, session=session)

        assert session.query(Setting).count() == 0

    @pytest.mark.usefixtures("tap")
    @pytest.mark.filterwarnings("ignore:Unknown setting:RuntimeWarning")
    def test_store_meltano_yml(self, subject, project) -> None:
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

    @pytest.mark.order(2)
    @pytest.mark.usefixtures("tap")
    def test_store_dotenv(
        self,
        subject: PluginSettingsService,
        project: Project,
    ) -> None:
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

        dotenv.set_key(project.dotenv, "TAP_MOCK_BOOLEAN", "false")
        project.refresh()
        assert subject.get_with_source("boolean") == (False, SettingValueStore.DOTENV)
        dotenv.unset_key(project.dotenv, "TAP_MOCK_BOOLEAN")

        subject.set("boolean", value=True, store=store)

        dotenv_contents = dotenv.dotenv_values(project.dotenv)
        assert dotenv_contents["TAP_MOCK_BOOLEAN"] == "true"
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

    @pytest.mark.usefixtures("tap")
    def test_env_var_expansion(
        self,
        session,
        subject: PluginSettingsService,
        project: Project,
        monkeypatch,
        env_var,
    ) -> None:
        if platform.system() == "Windows":
            pytest.xfail(
                "Fails on Windows: https://github.com/meltano/meltano/issues/3444",
            )
        monkeypatch.setenv("VAR", "hello world!")
        monkeypatch.setenv("FOO", "42")

        project.dotenv.touch()
        dotenv.set_key(project.dotenv, "A", "rock")
        dotenv.set_key(project.dotenv, "B", "paper")
        dotenv.set_key(project.dotenv, "C", "scissors")
        project.refresh()

        yml_config = {
            "var": "$VAR",
            "foo": "${FOO}",
            "missing": "$MISSING",
            "multiple": "$A ${B} $C",
            "info": "$MELTANO_EXTRACTOR_NAME",
            "password": "foo$r$6$bar",
            "user_agent": "$MELTANO_USER_AGENT",
            "_extra": "$TAP_MOCK_MULTIPLE",
            "_extra_generic": "$MELTANO_EXTRACT_FOO",
        }
        monkeypatch.setattr(subject.plugin, "config", yml_config)

        # Env vars inside env var values do not get expanded
        monkeypatch.setenv(env_var(subject, "test"), "$FOO")

        config = subject.as_dict(session=session)

        assert config["var"] == "hello world!"
        assert config["foo"] == "42"
        assert config["missing"] is None
        assert config["multiple"] == "rock paper scissors"
        assert config["info"] == "tap-mock"
        assert re.match(r"Meltano/\d+\.\d+\.\d+\S*", config["user_agent"])

        # Only `$ALL_CAPS` env vars are supported
        assert config["password"] == yml_config["password"]

        # Values of extras can reference regular settings
        assert config["_extra"] == config["multiple"]
        assert config["_extra_generic"] == config["foo"]

        # Env vars inside env var values do not get expanded
        assert config["test"] == "$FOO"

        # Expansion can be disabled
        config = subject.as_dict(session=session, expand_env_vars=False)
        assert yml_config == {
            key: value for key, value in config.items() if key in yml_config
        }

    @pytest.mark.order(3)
    @pytest.mark.usefixtures("tap")
    @pytest.mark.filterwarnings("ignore:Unknown setting:RuntimeWarning")
    def test_nested_keys(self, session, subject, project) -> None:
        def set_config(path, value) -> None:
            subject.set(path, value, store=SettingValueStore.MELTANO_YML)

        def unset_config(path) -> None:
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

    @pytest.mark.usefixtures("tap")
    @pytest.mark.filterwarnings("ignore:Unknown setting:RuntimeWarning")
    def test_custom_setting(self, session, subject, env_var) -> None:
        subject.set("custom_string", "from_yml", store=SettingValueStore.MELTANO_YML)
        subject.set("custom_bool", value=True, store=SettingValueStore.MELTANO_YML)
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

    def test_date_values(self, subject, monkeypatch) -> None:
        today = datetime.now(timezone.utc).date()
        monkeypatch.setitem(subject.plugin.config, "start_date", today)
        assert subject.get("start_date") == today.isoformat()

        now = datetime.now(timezone.utc)
        monkeypatch.setitem(subject.plugin.config, "start_date", now)
        assert subject.get("start_date") == now.isoformat()

    @pytest.mark.usefixtures("tap")
    @pytest.mark.filterwarnings("ignore:Unknown setting:RuntimeWarning")
    def test_kind_object(
        self,
        subject: PluginSettingsService,
        monkeypatch,
        env_var,
    ) -> None:
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

        assert subject.as_dict(process=False)["object"] == {
            "username": "from_meltano_yml",
            "password": "from_meltano_yml",
            "deep.nesting": "from_env",
        }
        assert subject.as_dict(process=True)["object"] == {
            "username": "from_meltano_yml",
            "password": "from_meltano_yml",
            "deep": {
                "nesting": "from_env",
            },
        }

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

    @pytest.mark.usefixtures("tap")
    def test_extra(self, subject, monkeypatch, env_var) -> None:
        subject._setting_defs = None

        assert "_select" in subject.as_dict()
        assert "_select" in subject.as_dict(extras=True)
        assert "_select" not in subject.as_dict(extras=False)

        assert subject.get_with_source("_select") == (
            ["*.*"],
            SettingValueStore.DEFAULT,
        )

        monkeypatch.setitem(
            subject.plugin.parent._variant.extras,
            "select",
            ["from_default"],
        )
        subject._setting_defs = None

        assert subject.get_with_source("_select") == (
            ["from_default"],
            SettingValueStore.DEFAULT,
        )

        monkeypatch.setitem(
            subject.plugin.config,
            "_select",
            ["from_meltano_yml_config"],
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

    @pytest.mark.usefixtures("environment")
    def test_extra_object(
        self,
        subject,
        monkeypatch,
        env_var,
        project_add_service,
        plugin_settings_service_factory,
    ) -> None:
        try:
            transform = project_add_service.add(
                PluginType.TRANSFORMS,
                "tap-mock-transform",
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

        subject.set(
            "_vars",
            {"other": "from_meltano_yml"},
            store=SettingValueStore.MELTANO_YML,
        )

        assert subject.get_with_source("_vars") == (
            {"var": "from_default", "other": "from_meltano_yml"},
            SettingValueStore.MELTANO_YML,
        )

        with monkeypatch.context() as patch:
            patch.setenv(env_var(subject, "_vars.var"), "from_env")
            assert subject.get_with_source("_vars") == (
                {"var": "from_env", "other": "from_meltano_yml"},
                SettingValueStore.ENV,
            )

        with monkeypatch.context() as patch:
            patch.setenv(env_var(subject, "_vars"), '{"var": "from_env"}')
            assert subject.get_with_source("_vars") == (
                {"var": "from_env"},
                SettingValueStore.ENV,
            )

        subject.set(
            "_vars",
            {"dev_setting": "from_dev_env"},
            store=SettingValueStore.MELTANO_ENVIRONMENT,
        )
        assert subject.get_with_source("_vars") == (
            {
                "var": "from_default",
                "other": "from_meltano_yml",
                "dev_setting": "from_dev_env",
            },
            SettingValueStore.MELTANO_ENVIRONMENT,
        )

        subject.project.deactivate_environment()

        inherited = project_add_service.add(
            PluginType.TRANSFORMS,
            "tap-mock-transform--inherited",
            inherit_from=transform.name,
        )
        inherited_subject = plugin_settings_service_factory(inherited)
        inherited_subject.set("_vars", {"new": "from_inheriting"})

        assert inherited_subject.get_with_source("_vars") == (
            {
                "other": "from_meltano_yml",
                "new": "from_inheriting",
            },
            SettingValueStore.MELTANO_YML,
        )

    def test_find_setting_raises_with_conflicting(
        self,
        tap,
        plugin_settings_service_factory,
        monkeypatch,
    ) -> None:
        subject = plugin_settings_service_factory(tap)
        monkeypatch.setenv("TAP_MOCK_ALIASED", "value_0")
        monkeypatch.setenv("TAP_MOCK_ALIASED_1", "value_1")
        with pytest.raises(ConflictingSettingValueException):
            subject.get("aliased")

    def test_find_setting_raises_with_multiple(
        self,
        tap,
        plugin_settings_service_factory,
        monkeypatch,
    ) -> None:
        subject = plugin_settings_service_factory(tap)
        monkeypatch.setenv("TAP_MOCK_ALIASED", "value_0")
        monkeypatch.setenv("TAP_MOCK_ALIASED_1", "value_0")
        with pytest.raises(MultipleEnvVarsSetException):
            subject.get("aliased")

    def test_find_setting_aliases(self, tap, plugin_settings_service_factory) -> None:
        subject = plugin_settings_service_factory(tap)
        subject.set("aliased_3", "value_3")
        assert subject.get("aliased") == "value_3"

    @pytest.mark.order(-1)
    def test_strict_env_var_mode_on_raises_error(self, subject) -> None:
        subject.project_settings_service.set(
            [FEATURE_FLAG_PREFIX, str(FeatureFlags.STRICT_ENV_VAR_MODE)],
            value=True,
        )
        subject.set("stacked_env_var", "${NONEXISTENT_ENV_VAR}")
        with pytest.raises(EnvironmentVariableNotSetError):
            subject.get("stacked_env_var")

    @pytest.mark.order(-1)
    def test_strict_env_var_mode_off_no_raise_error(self, subject) -> None:
        subject.project_settings_service.set(
            [FEATURE_FLAG_PREFIX, str(FeatureFlags.STRICT_ENV_VAR_MODE)],
            value=False,
        )
        subject.set("stacked_env_var", "${NONEXISTENT_ENV_VAR}")
        assert subject.get("stacked_env_var") is None
