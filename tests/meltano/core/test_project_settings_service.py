from __future__ import annotations

import warnings

import pytest

from meltano.core.environment import Environment
from meltano.core.project_settings_service import (
    ProjectSettingsService,
    SettingValueStore,
)
from meltano.core.settings_service import (
    EXPERIMENTAL,
    FEATURE_FLAG_PREFIX,
    FeatureFlags,
    FeatureNotAllowedException,
)
from meltano.core.utils import EnvironmentVariableNotSetError


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
    @pytest.fixture()
    def environment(self):
        return Environment("testing", {})

    def test_get_with_source(self, subject, monkeypatch):
        # A warning is raised because the setting does not exist.
        with pytest.warns(RuntimeWarning):
            assert subject.get_with_source(
                "and_now_for_something_completely_different"
            ) == (None, SettingValueStore.DEFAULT)

        def assert_value_source(value, source):
            assert subject.get_with_source("project_id") == (value, source)

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

    def test_strict_env_var_mode_on_raises_error(self, subject):
        subject.set([FEATURE_FLAG_PREFIX, str(FeatureFlags.STRICT_ENV_VAR_MODE)], True)
        subject.set(
            "stacked_env_var",
            "${NONEXISTENT_ENV_VAR}@nonexistent",
        )
        with pytest.raises(EnvironmentVariableNotSetError):
            subject.get("stacked_env_var")

    def test_strict_env_var_mode_off_no_raise_error(self, subject):
        subject.set([FEATURE_FLAG_PREFIX, str(FeatureFlags.STRICT_ENV_VAR_MODE)], False)
        subject.set(
            "stacked_env_var",
            "${NONEXISTENT_ENV_VAR}@nonexistent_1",
        )
        assert subject.get("stacked_env_var") == "@nonexistent_1"

    def test_warn_if_default_setting_is_used(self, subject, monkeypatch):
        # Assert that warnings are not raised in the following cases:
        with warnings.catch_warnings():
            warnings.simplefilter("error")

            for ff in FeatureFlags:
                subject.get(f"{FEATURE_FLAG_PREFIX}.{ff}")

            subject.get("project_id")
            subject.get("disable_tracking")

            ProjectSettingsService.config_override.pop(
                "send_anonymous_usage_stats", None
            )
            subject.config_override.pop("send_anonymous_usage_stats", None)
            subject.unset("send_anonymous_usage_stats")

            monkeypatch.setenv("MELTANO_SEND_ANONYMOUS_USAGE_STATS", "True")
            assert subject.get("send_anonymous_usage_stats")
            monkeypatch.setenv("MELTANO_SEND_ANONYMOUS_USAGE_STATS", "False")
            assert not subject.get("send_anonymous_usage_stats")
            monkeypatch.delenv("MELTANO_SEND_ANONYMOUS_USAGE_STATS")
            subject.get("send_anonymous_usage_stats")

        # Assert that warnings are raised in the following cases:
        for setting in (
            "projectID",
            "tracking_disabled",
            "MELTANO_SEND_ANONYMOUS_USAGE_STATS",
            "send_anon_usage_stats",
        ):
            with pytest.warns(RuntimeWarning):
                subject.get(setting)

    def test_meltano_settings_with_active_environment(
        self, subject, monkeypatch, environment
    ):
        # make sure that meltano setting values are written to the root of `meltano.yml`
        # even if there is an active environment
        monkeypatch.setattr(subject.project, "active_environment", environment)
        assert subject.project.active_environment == environment
        subject.set("database_max_retries", 10000)
        value, source = subject.get_with_source("database_max_retries")
        assert source == SettingValueStore.MELTANO_YML
        assert value == 10000

    def test_fully_missing_env_var_setting_is_none(
        self, subject: ProjectSettingsService
    ):
        subject.set([FEATURE_FLAG_PREFIX, str(FeatureFlags.STRICT_ENV_VAR_MODE)], False)
        # https://github.com/meltano/meltano/issues/7189#issuecomment-1396112167
        with pytest.warns(RuntimeWarning, match="Unknown setting 'port'"):
            subject.set("port", "${UNSET_PORT_ENV_VAR}")
        assert subject.get("port") is None
