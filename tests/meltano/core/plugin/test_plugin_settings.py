import pytest

from meltano.core.plugin.setting import PluginSetting
from meltano.core.plugin.settings_service import PluginSettingValueSource


def test_create(session):
    setting = PluginSetting(
        name="api_key.test.test", namespace="gitlab", value="C4F3C4F3", enabled=True
    )

    session.add(setting)
    session.commit()

    fetched = session.query(PluginSetting).first()
    assert setting == fetched


@pytest.fixture
def subject(session, project_add_service, tap, plugin_settings_service_factory):
    plugin = project_add_service.add("extractors", tap.name)

    return plugin_settings_service_factory(session)


class TestPluginSettingsService:
    def test_get_value(self, session, subject, project, tap, monkeypatch):
        # returns the default value when unset
        assert subject.get_value(tap, "test") == (
            "mock",
            PluginSettingValueSource.DEFAULT,
        )

        # overriden by an PluginSetting db value when set
        setting = subject.set(tap, "test", "THIS_IS_FROM_DB")
        assert subject.get_value(tap, "test") == (
            "THIS_IS_FROM_DB",
            PluginSettingValueSource.DB,
        )

        # but only if enabled
        setting.enabled = False
        session.merge(setting)
        session.commit()
        assert subject.get_value(tap, "test") == (
            "mock",
            PluginSettingValueSource.DEFAULT,
        )

        # overriden via the `meltano.yml` configuration
        project._meltano["plugins"]["extractors"][0]["config"] = {"test": 42}
        assert subject.get_value(tap, "test") == (
            42,
            PluginSettingValueSource.MELTANO_YML,
        )
        project.reload()

        # overriden via ENV
        monkeypatch.setenv("PYTEST_TEST", "N33DC0F33")
        assert subject.get_value(tap, "test") == (
            "N33DC0F33",
            PluginSettingValueSource.ENV,
        )

    def test_as_config(self, subject, tap):
        assert subject.as_config(tap) == {"test": "mock", "start_date": None}

    def test_as_env(self, subject, tap):
        assert subject.as_env(tap) == {
            "PYTEST_TEST": "mock",
            "PYTEST_START_DATE": "None",
        }

    def test_unset(self, session, subject, tap):
        # overriden by an PluginSetting db value when set
        setting = subject.set(tap, "test", "THIS_IS_FROM_DB")
        assert session.query(PluginSetting).count() == 1

        subject.unset(tap, "test")
        assert session.query(PluginSetting).count() == 0


class TestCustomPluginSettingsService:
    @pytest.fixture(scope="class", autouse=True)
    def custom_setting(subject, project, config_service, tap):
        with project.meltano_update() as meltano:
            custom_settings = [
                {
                    "name": "custom_setting",
                    "value": "pytest",
                    "kind": "pytest",
                    "env": "PYTEST_CUSTOM_SETTING",
                },
                {"name": "test", "value": "override"},
            ]

            tap_mock = meltano["plugins"]["extractors"][0]
            tap_mock["settings"] = custom_settings

    def test_setting_exists(self, subject, tap):
        exists = lambda setting: setting["name"] == "custom_setting"

        assert any(map(exists, subject.definitions(tap)))

    def test_precedence(self, subject, tap):
        value, _ = subject.get_value(tap, "test")

        assert value == "override"
