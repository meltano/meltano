import pytest

from meltano.core.project import Project
from meltano.core.project_settings_service import (
    ProjectSettingsService,
    SettingValueStore,
)


@pytest.fixture
def config_override():
    try:
        ProjectSettingsService.config_override["project_id"] = "from_config_override"

        yield
    finally:
        ProjectSettingsService.config_override.pop("project_id")


@pytest.fixture
def subject(project):
    return ProjectSettingsService(project)


class TestProjectSettingsService:
    def test_get_with_source(self, subject, monkeypatch):
        def assert_value_source(value, source):
            assert subject.get_with_source("project_id") == (value, source)

        assert_value_source(None, SettingValueStore.DEFAULT)

        subject.set(
            "project_id", "from_meltano_yml", store=SettingValueStore.MELTANO_YML
        )

        assert_value_source("from_meltano_yml", SettingValueStore.MELTANO_YML)

        subject.set("project_id", "from_dotenv", store=SettingValueStore.DOTENV)

        assert_value_source("from_dotenv", SettingValueStore.DOTENV)

        with monkeypatch.context() as m:
            env_key = subject.setting_env(subject.find_setting("project_id"))
            m.setenv(env_key, "from_env")

            assert_value_source("from_env", SettingValueStore.ENV)

    def test_get_with_source_config_override(self, config_override, subject):
        assert subject.get_with_source("project_id") == (
            "from_config_override",
            SettingValueStore.CONFIG_OVERRIDE,
        )

    def test_get_with_source_ui_cfg(self, project, subject, monkeypatch):
        def assert_value_source(value, source):
            assert subject.get_with_source("ui.server_name") == (value, source)

        assert_value_source(None, SettingValueStore.DEFAULT)

        project.root_dir("ui.cfg").write_text("SERVER_NAME = None")

        assert_value_source(None, SettingValueStore.DEFAULT)

        project.root_dir("ui.cfg").write_text("SERVER_NAME = 'from_ui_cfg'")

        assert_value_source("from_ui_cfg", SettingValueStore.ENV)

        with monkeypatch.context() as m:
            m.setenv(
                subject.setting_env(subject.find_setting("ui.server_name")), "from_env"
            )

            assert_value_source("from_env", SettingValueStore.ENV)
