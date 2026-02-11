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
    @pytest.fixture
    def environment(self):
        return Environment("testing", {})

    def test_get_with_source(self, subject, monkeypatch) -> None:
        # A warning is raised because the setting does not exist.
        with pytest.warns(RuntimeWarning):
            assert subject.get_with_source(
                "and_now_for_something_completely_different",
            ) == (None, SettingValueStore.DEFAULT)

        def assert_value_source(value, source) -> None:
            assert subject.get_with_source("project_id") == (value, source)

        subject.set(
            "project_id",
            "from_meltano_yml",
            store=SettingValueStore.MELTANO_YML,
        )

        assert_value_source("from_meltano_yml", SettingValueStore.MELTANO_YML)

        subject.set("project_id", "from_dotenv", store=SettingValueStore.DOTENV)

        assert_value_source("from_dotenv", SettingValueStore.DOTENV)

        with monkeypatch.context() as ctx:
            env_key = subject.setting_env(subject.find_setting("project_id"))
            ctx.setenv(env_key, "from_env")

            assert_value_source("from_env", SettingValueStore.ENV)

    @pytest.mark.usefixtures("config_override")
    def test_get_with_source_config_override(self, subject) -> None:
        assert subject.get_with_source("project_id") == (
            "from_config_override",
            SettingValueStore.CONFIG_OVERRIDE,
        )

    def test_experimental_on(self, subject, monkeypatch) -> None:
        changed = []
        monkeypatch.setenv("MELTANO_EXPERIMENTAL", "true")
        with subject.feature_flag(EXPERIMENTAL):
            changed.append(True)
        assert changed

    def test_experimental_off_by_default(self, subject) -> None:
        changed = []
        with (
            pytest.raises(FeatureNotAllowedException),
            subject.feature_flag(EXPERIMENTAL),
        ):
            changed.append(True)

    @pytest.mark.filterwarnings("ignore:Unknown setting 'ff.allowed':RuntimeWarning")
    def test_feature_flag_allowed(self, subject) -> None:
        changed = []
        subject.set([FEATURE_FLAG_PREFIX, "allowed"], value=True)

        @subject.feature_flag("allowed")
        def should_run() -> None:
            changed.append(True)

        should_run()
        assert changed

    @pytest.mark.filterwarnings("ignore:Unknown setting 'ff.disallowed':RuntimeWarning")
    def test_feature_flag_disallowed(self, subject) -> None:
        changed = []
        subject.set([FEATURE_FLAG_PREFIX, "disallowed"], value=False)

        @subject.feature_flag("disallowed")
        def should_not_run() -> None:
            changed.append(True)

        with pytest.raises(FeatureNotAllowedException):
            should_not_run()

    @pytest.mark.filterwarnings(
        "ignore:Unknown setting 'stacked_env_var':RuntimeWarning",
    )
    def test_strict_env_var_mode_on_raises_error(self, subject) -> None:
        subject.set(
            [FEATURE_FLAG_PREFIX, str(FeatureFlags.STRICT_ENV_VAR_MODE)],
            value=True,
        )
        subject.set(
            "stacked_env_var",
            "${NONEXISTENT_ENV_VAR}@nonexistent",
        )
        with pytest.raises(EnvironmentVariableNotSetError):
            subject.get("stacked_env_var")

    @pytest.mark.filterwarnings(
        "ignore:Unknown setting 'stacked_env_var':RuntimeWarning",
    )
    def test_strict_env_var_mode_off_no_raise_error(self, subject) -> None:
        subject.set(
            [FEATURE_FLAG_PREFIX, str(FeatureFlags.STRICT_ENV_VAR_MODE)],
            value=False,
        )
        subject.set(
            "stacked_env_var",
            "${NONEXISTENT_ENV_VAR}@nonexistent_1",
        )
        assert subject.get("stacked_env_var") == "@nonexistent_1"

    def test_warn_if_default_setting_is_used(self, subject, monkeypatch) -> None:
        # Assert that warnings are not raised in the following cases:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "error",
                "Unknown setting",
                RuntimeWarning,
            )
            warnings.filterwarnings(
                "ignore",
                "The 'version' field in meltano.yml is deprecated.*",
                DeprecationWarning,
            )

            for ff in FeatureFlags:
                subject.get(f"{FEATURE_FLAG_PREFIX}.{ff}")

            subject.get("project_id")
            subject.get("disable_tracking")

            ProjectSettingsService.config_override.pop(
                "send_anonymous_usage_stats",
                None,
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
        self,
        subject,
        monkeypatch,
        environment,
    ) -> None:
        # make sure that meltano setting values are written to the root of `meltano.yml`
        # even if there is an active environment
        monkeypatch.setattr(subject.project, "environment", environment)
        assert subject.project.environment == environment
        subject.set("database_max_retries", 10000)
        value, source = subject.get_with_source("database_max_retries")
        assert source == SettingValueStore.MELTANO_YML
        assert value == 10000

    def test_fully_missing_env_var_setting_is_none(
        self,
        subject: ProjectSettingsService,
    ) -> None:
        subject.set(
            [FEATURE_FLAG_PREFIX, str(FeatureFlags.STRICT_ENV_VAR_MODE)],
            value=False,
        )
        # https://github.com/meltano/meltano/issues/7189#issuecomment-1396112167
        with pytest.warns(RuntimeWarning, match="Unknown setting 'port'"):
            subject.set("port", "${UNSET_PORT_ENV_VAR}")
        assert subject.get("port") is None

    def test_env_var_settings_expanded_before_cast(
        self,
        subject: ProjectSettingsService,
    ) -> None:
        name = "database_max_retries"  # Using this because it's an int setting
        setting_def = subject.find_setting(name)

        subject.set(name, setting_def.value, setting_def=setting_def)
        assert subject.get(name) == setting_def.value

        SettingValueStore.MELTANO_YML.manager(subject).set(
            name,
            [name],
            "$DB_MAX_RETRIES_TEST",
            setting_def=setting_def,
        )

        subject.set(
            [FEATURE_FLAG_PREFIX, str(FeatureFlags.STRICT_ENV_VAR_MODE)],
            value=False,
        )
        assert subject.get(name) is None

        subject.env_override["DB_MAX_RETRIES_TEST"] = "7"
        assert subject.get(name) == 7
