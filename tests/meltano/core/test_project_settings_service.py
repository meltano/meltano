import pytest

from meltano.core.project import Project
from meltano.core.project_settings_service import (
    ProjectSettingsService,
    SettingValueSource,
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
def dotenv(project):
    project.dotenv.write_text(f"MELTANO_PROJECT_ID=from_dotenv")


@pytest.fixture
def subject(project):
    return ProjectSettingsService(project)


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
            m.setenv("MELTANO_PROJECT_ID", "from_env")

            assert_value_source("from_env", SettingValueSource.ENV)

    def test_get_with_source_dotenv(self, dotenv, project, subject, monkeypatch):
        # Ensure .env is loaded again
        Project.activate(project)

        def assert_value_source(value, source):
            assert subject.get_with_source("project_id") == (value, source)

        assert_value_source("from_dotenv", SettingValueSource.ENV)

        with monkeypatch.context() as m:
            m.setenv("MELTANO_PROJECT_ID", "from_env")

            assert_value_source("from_env", SettingValueSource.ENV)

    def test_get_with_source_config_override(self, config_override, subject):
        assert subject.get_with_source("project_id") == (
            "from_config_override",
            SettingValueSource.CONFIG_OVERRIDE,
        )

    def test_get_with_source_ui_cfg(self, project, subject, monkeypatch):
        def assert_value_source(value, source):
            assert subject.get_with_source("ui.server_name") == (value, source)

        assert_value_source(None, SettingValueSource.DEFAULT)

        project.root_dir("ui.cfg").write_text("SERVER_NAME = None")

        assert_value_source(None, SettingValueSource.DEFAULT)

        project.root_dir("ui.cfg").write_text("SERVER_NAME = 'from_ui_cfg'")

        assert_value_source("from_ui_cfg", SettingValueSource.ENV)

        with monkeypatch.context() as m:
            m.setenv(
                subject.setting_env(subject.find_setting("ui.server_name")), "from_env"
            )

            assert_value_source("from_env", SettingValueSource.ENV)
