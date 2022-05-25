import pytest

from meltano.core.project_settings_service import (
    ProjectSettingsService,
    SettingValueStore,
)
from meltano.core.settings_service import (
    EXPERIMENTAL,
    FEATURE_FLAG_PREFIX,
    FeatureNotAllowedException,
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

        with monkeypatch.context() as ctx:
            env_key = subject.setting_env(subject.find_setting("project_id"))
            ctx.setenv(env_key, "from_env")

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

        with monkeypatch.context() as ctx:
            ctx.setenv(
                subject.setting_env(subject.find_setting("ui.server_name")), "from_env"
            )

            assert_value_source("from_env", SettingValueStore.ENV)

    def test_experimental_on(self, subject, monkeypatch):
        changed = []
        monkeypatch.setenv("MELTANO_EXPERIMENTAL", "true")
        with subject.feature_flag(EXPERIMENTAL):
            changed.append(True)
        assert changed

    def test_experimental_off_by_default(self, subject, monkeypatch):
        changed = []
        with pytest.raises(FeatureNotAllowedException):
            with subject.feature_flag(EXPERIMENTAL):
                changed.append(True)

    def test_feature_flag_allowed(self, subject):
        changed = []
        subject.set([FEATURE_FLAG_PREFIX, "allowed"], True)

        @subject.feature_flag("allowed")
        def should_run():
            changed.append(True)

        should_run()
        assert changed

    def test_feature_flag_disallowed(self, subject):
        changed = []
        subject.set([FEATURE_FLAG_PREFIX, "disallowed"], False)

        @subject.feature_flag("disallowed")
        def should_not_run():
            changed.append(True)

        with pytest.raises(FeatureNotAllowedException):
            should_not_run()
