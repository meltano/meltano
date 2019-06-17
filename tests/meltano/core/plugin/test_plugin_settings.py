import pytest

from meltano.core.plugin.setting import PluginSetting


def test_create(session):
    setting = PluginSetting(
        name="api_key.test.test", namespace="gitlab", value="C4F3C4F3", enabled=True
    )

    session.add(setting)
    session.commit()

    fetched = session.query(PluginSetting).first()
    assert setting == fetched


class TestPluginSettingsService:
    @pytest.fixture
    def subject(self, project, project_add_service, plugin_settings_service):
        project_add_service.add("extractors", "tap-mock")

        return plugin_settings_service

    def test_get_value(self, subject, project, monkeypatch):
        session = subject._session_cls()

        # returns the default value when unset
        assert subject.get_value("test") == "mock"

        # overriden by an PluginSetting db value when set
        setting = subject.set("test", "THIS_IS_FROM_DB")
        assert subject.get_value("test") == "THIS_IS_FROM_DB"

        # but only if enabled
        setting.enabled = False
        session.merge(setting)
        session.commit()
        assert subject.get_value("test") == "mock"

        # overriden via the `meltano.yml` configuration
        with project.meltano_update() as meltano:
            meltano["plugins"]["extractors"][0]["config"] = {"test": 42}

        assert subject.get_value("test") == 42

        # overriden via ENV
        monkeypatch.setenv("PYTEST_TEST", "N33DC0F33")
        assert subject.get_value("test") == "N33DC0F33"

    def test_as_config(self, subject):
        assert subject.as_config() == {"test": "mock"}

    def test_unset(self, subject, session):
        # overriden by an PluginSetting db value when set
        setting = subject.set("test", "THIS_IS_FROM_DB")
        assert subject._session_cls().query(PluginSetting).count() == 1

        subject.unset("test")
        assert subject._session_cls().query(PluginSetting).count() == 0
