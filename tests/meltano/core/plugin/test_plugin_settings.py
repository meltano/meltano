import pytest

from meltano.core.plugin import PluginRef, PluginType, PluginInstall
from meltano.core.plugin.setting import PluginSetting
from meltano.core.plugin.settings_service import (
    PluginSettingValueSource,
    REDACTED_VALUE,
)


def test_create(session):
    setting = PluginSetting(
        name="api_key.test.test", namespace="gitlab", value="C4F3C4F3", enabled=True
    )

    session.add(setting)
    session.commit()

    fetched = session.query(PluginSetting).first()
    assert setting == fetched


@pytest.fixture(scope="class")
def env_var(plugin_discovery_service, plugin_settings_service):
    def _wrapper(plugin: PluginRef, setting_name):
        plugin_def = plugin_discovery_service.find_plugin(plugin.type, plugin.name)
        setting_def = plugin_settings_service.find_setting(plugin, setting_name)

        return plugin_settings_service.setting_env(setting_def, plugin_def)

    return _wrapper


@pytest.fixture
def subject(session, project_add_service, tap, plugin_settings_service):
    plugin = project_add_service.add("extractors", tap.name)

    return plugin_settings_service


class TestPluginSettingsService:
    def test_get_value(
        self, session, subject, project, tap, env_var, monkeypatch, config_service
    ):
        profile = tap.add_profile("profile", label="Profile")
        config_service.update_plugin(tap)
        tap_with_profile = config_service.find_plugin(tap.name)
        tap_with_profile.use_profile(profile)

        # returns the default value when unset
        assert subject.get_value(session, tap, "test") == (
            "mock",
            PluginSettingValueSource.DEFAULT,
        )
        assert subject.get_value(session, tap_with_profile, "test") == (
            "mock",
            PluginSettingValueSource.DEFAULT,
        )

        # overriden by an PluginSetting db value when set
        setting = subject.set(session, tap, "test", "THIS_IS_FROM_DB")
        setting_with_profile = subject.set(
            session, tap_with_profile, "test", "THIS_IS_FROM_DB_WITH_PROFILE"
        )

        assert subject.get_value(session, tap, "test") == (
            "THIS_IS_FROM_DB",
            PluginSettingValueSource.DB,
        )
        assert subject.get_value(session, tap_with_profile, "test") == (
            "THIS_IS_FROM_DB_WITH_PROFILE",
            PluginSettingValueSource.DB,
        )

        # but only if enabled
        setting.enabled = False
        setting_with_profile.enabled = False
        session.merge(setting)
        session.merge(setting_with_profile)
        session.commit()

        assert subject.get_value(session, tap, "test") == (
            "mock",
            PluginSettingValueSource.DEFAULT,
        )
        assert subject.get_value(session, tap_with_profile, "test") == (
            "mock",
            PluginSettingValueSource.DEFAULT,
        )

        # overriden via the `meltano.yml` configuration
        with project.meltano_update() as meltano:
            extractor = meltano.plugins.extractors[0]
            extractor.config = {"test": 42}
            extractor.get_profile("profile").config = {"test": 43}

        assert subject.get_value(session, tap, "test") == (
            42,
            PluginSettingValueSource.MELTANO_YML,
        )
        assert subject.get_value(session, tap_with_profile, "test") == (
            43,
            PluginSettingValueSource.MELTANO_YML,
        )

        # revert back to the original
        with project.meltano_update() as meltano:
            extractor = meltano.plugins.extractors[0]
            extractor.config = {}
            extractor.get_profile("profile").config = {}

        # overriden via ENV
        monkeypatch.setenv(env_var(tap, "test"), "N33DC0F33")

        assert subject.get_value(session, tap, "test") == (
            "N33DC0F33",
            PluginSettingValueSource.ENV,
        )
        assert subject.get_value(session, tap_with_profile, "test") == (
            "N33DC0F33",
            PluginSettingValueSource.ENV,
        )

    def test_as_config_custom(self, subject, session, config_service):
        EXPECTED = {"test": "custom", "start_date": None, "secure": None}
        tap = PluginInstall(
            PluginType.EXTRACTORS,
            name="tap-custom",
            namespace="tap_custom",
            config=EXPECTED,
        )
        config_service.add_to_file(tap)

        assert subject.as_config(session, tap) == EXPECTED

    def test_as_config(self, subject, session, tap):
        EXPECTED = {"test": "mock", "start_date": None, "secure": None}
        full_config = subject.as_config(session, tap)
        redacted_config = subject.as_config(session, tap, redacted=True)

        for k, v in EXPECTED.items():
            assert full_config.get(k) == v
            assert redacted_config.get(k) == v

    def test_as_config_redacted(self, subject, session, tap):
        # ensure values are redacted when they are set
        subject.set(session, tap, "secure", "thisisatest")
        config = subject.as_config(session, tap, redacted=True)

        assert config["secure"] == REDACTED_VALUE

        # although setting the REDACTED_VALUE does nothing
        subject.set(session, tap, "secure", REDACTED_VALUE)
        config = subject.as_config(session, tap)
        assert config["secure"] == "thisisatest"

    def test_as_env(self, subject, session, tap, env_var):
        config = subject.as_env(session, tap)

        assert config.get(env_var(tap, "test")) == "mock"
        assert config.get(env_var(tap, "start_date")) == "None"
        assert config.get(env_var(tap, "secure")) == "None"

    def test_unset(self, session, subject, tap):
        # overriden by an PluginSetting db value when set
        setting = subject.set(session, tap, "test", "THIS_IS_FROM_DB")
        assert session.query(PluginSetting).count() == 1

        subject.unset(session, tap, "test")
        assert session.query(PluginSetting).count() == 0
