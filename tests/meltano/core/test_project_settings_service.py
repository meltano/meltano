import pytest

from meltano.core.project_settings_service import (
    ProjectSettingsService,
    SettingValueSource,
    SettingValueStore,
)


@pytest.fixture
def subject(project):
    return ProjectSettingsService(project)


@pytest.fixture
def config_override():
    try:
        ProjectSettingsService.config_override["project_id"] = "from_config_override"

        yield
    finally:
        ProjectSettingsService.config_override.pop("project_id")


class TestProjectSettingsService:
    def test_get_with_source(self, subject, monkeypatch):
        def assert_value_source(value, source):
            assert subject.get_with_source("project_id") == (value, source)

        assert_value_source(None, SettingValueSource.DEFAULT)

        subject.set(
            "project_id", "from_meltano_yml", store=SettingValueStore.MELTANO_YML
        )

        assert_value_source("from_meltano_yml", SettingValueSource.MELTANO_YML)

        with monkeypatch.context() as m:
            m.setenv(
                subject.setting_env(subject.find_setting("project_id")), "from_env"
            )

            assert_value_source("from_env", SettingValueSource.ENV)

    def test_get_with_source_config_override(self, config_override, subject):
        assert subject.get_with_source("project_id") == (
            "from_config_override",
            SettingValueSource.CONFIG_OVERRIDE,
        )
