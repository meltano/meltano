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

        subject.set("project_id", "from_dotenv", store=SettingValueStore.DOTENV)

        assert_value_source("from_dotenv", SettingValueSource.DOTENV)

        with monkeypatch.context() as m:
            env_key = subject.setting_env(subject.find_setting("project_id"))
            m.setenv(env_key, "from_env")

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

    def test_path_prefix(self, session, subject):
        assert not subject.path_prefix
        assert not subject.name_prefix

        subject.set("project_id", "from_dotenv", store=SettingValueStore.DOTENV)
        subject.set("project_id", "from_yml", store=SettingValueStore.MELTANO_YML)
        subject.set(
            "project_id", "from_db", store=SettingValueStore.DB, session=session
        )

        subject.set("ui.server_name", "from_yml", store=SettingValueStore.MELTANO_YML)
        subject.set("ui.custom", "from_yml", store=SettingValueStore.MELTANO_YML)
        subject.set("ui.custom", "from_dotenv", store=SettingValueStore.DOTENV)

        assert subject.get_with_source("project_id") == (
            "from_dotenv",
            SettingValueSource.DOTENV,
        )

        subject.path_prefix = ["ui"]
        assert subject.name_prefix == "ui."

        # definitions
        definition_names = [setting_def.name for setting_def in subject.definitions()]
        assert all(setting_name.startswith("ui.") for setting_name in definition_names)
        assert "ui.server_name" in definition_names
        assert "ui.custom" in definition_names

        # config_with_metadata
        config_keys = subject.config_with_metadata().keys()
        assert all(setting_name.startswith("ui.") for setting_name in config_keys)
        assert "ui.server_name" in config_keys
        assert "ui.custom" in config_keys

        # as_dict
        dict_keys = subject.as_dict().keys()
        assert all(setting_name.startswith("ui.") for setting_name in dict_keys)
        assert "ui.server_name" in dict_keys
        assert "ui.custom" in dict_keys

        # as_env
        env_keys = subject.as_env().keys()
        assert all(setting_name.startswith("MELTANO_UI_") for setting_name in env_keys)
        assert "MELTANO_UI_SERVER_NAME" in env_keys
        assert "MELTANO_UI_CUSTOM" in env_keys

        # get_with_source
        assert subject.get_with_source("project_id") == (
            None,
            SettingValueSource.DEFAULT,
        )
        assert subject.get_with_source("server_name") == (
            "from_yml",
            SettingValueSource.MELTANO_YML,
        )
        assert subject.get_with_source("custom") == (
            "from_dotenv",
            SettingValueSource.DOTENV,
        )

        # get
        assert subject.get("server_name") == "from_yml"
        assert subject.get("custom") == "from_dotenv"

        # set
        subject.set("server_name", "from_dotenv", store=SettingValueStore.DOTENV)

        assert subject.get_with_source("server_name") == (
            "from_dotenv",
            SettingValueSource.DOTENV,
        )

        subject.set(
            "server_name", "from_db", store=SettingValueStore.DB, session=session
        )

        # unset
        subject.unset("server_name", store=SettingValueStore.DOTENV)

        assert subject.get_with_source("server_name") == (
            "from_yml",
            SettingValueSource.MELTANO_YML,
        )

        subject.unset("server_name", store=SettingValueStore.MELTANO_YML)

        assert subject.get_with_source("server_name", session=session) == (
            "from_db",
            SettingValueSource.DB,
        )

        subject.unset("server_name", store=SettingValueStore.DB, session=session)

        assert subject.get_with_source("server_name", session=session) == (
            None,
            SettingValueSource.DEFAULT,
        )

        # reset
        subject.set("server_name", "from_dotenv", store=SettingValueStore.DOTENV)
        subject.set("server_name", "from_yml", store=SettingValueStore.MELTANO_YML)
        subject.set(
            "server_name", "from_db", store=SettingValueStore.DB, session=session
        )

        assert subject.get_with_source("server_name") == (
            "from_dotenv",
            SettingValueSource.DOTENV,
        )
        assert subject.get_with_source("custom") == (
            "from_dotenv",
            SettingValueSource.DOTENV,
        )

        subject.reset(store=SettingValueStore.DOTENV)

        assert subject.get_with_source("server_name") == (
            "from_yml",
            SettingValueSource.MELTANO_YML,
        )
        assert subject.get_with_source("custom") == (
            "from_yml",
            SettingValueSource.MELTANO_YML,
        )

        subject.reset(store=SettingValueStore.MELTANO_YML)

        assert subject.get_with_source("server_name", session=session) == (
            "from_db",
            SettingValueSource.DB,
        )
        assert subject.get_with_source("custom") == (None, SettingValueSource.DEFAULT)

        subject.reset(store=SettingValueStore.DB, session=session)

        assert subject.get_with_source("server_name", session=session) == (
            None,
            SettingValueSource.DEFAULT,
        )

        subject.path_prefix = []

        assert subject.get_with_source("project_id") == (
            "from_dotenv",
            SettingValueSource.DOTENV,
        )

        subject.reset(store=SettingValueStore.DOTENV)

        assert subject.get_with_source("project_id") == (
            "from_yml",
            SettingValueSource.MELTANO_YML,
        )

        subject.reset(store=SettingValueStore.MELTANO_YML)

        assert subject.get_with_source("project_id", session=session) == (
            "from_db",
            SettingValueSource.DB,
        )

        subject.reset(store=SettingValueStore.DB, session=session)

        assert subject.get_with_source("project_id", session=session) == (
            None,
            SettingValueSource.DEFAULT,
        )
