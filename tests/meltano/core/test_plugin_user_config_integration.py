"""End-to-end tests for plugin user configuration integration."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

from meltano.core.settings_store import SettingValueStore
from meltano.core.yaml_config import YamlConfigLoader


class TestPluginUserConfigEndToEnd:
    """End-to-end tests for plugin user configuration."""

    def test_plugin_settings_service_reads_user_config(
        self,
        session,
        tap,
        plugin_settings_service_factory,
    ):
        """Test that PluginSettingsService reads from user config."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".meltanorc", delete=False
        ) as temp_file:
            config_content = """plugins:
  extractors:
    tap-mock:
      test: "user-config-value"
      password: "user-config-password"
"""
            temp_file.write(config_content)
            temp_file.flush()

            try:
                # Patch the user config path to use our temporary file
                with patch.object(
                    YamlConfigLoader,
                    "_get_user_config_path",
                    return_value=Path(temp_file.name),
                ):
                    # Create PluginSettingsService using the fixture
                    settings_service = plugin_settings_service_factory(tap)

                    # Test that values are read from user config
                    assert settings_service.get("test") == "user-config-value"
                    assert settings_service.get("password") == "user-config-password"

                    # Test that non-existent values return None (with warning)
                    import warnings

                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", RuntimeWarning)
                        assert settings_service.get("non_existent") is None

            finally:
                Path(temp_file.name).unlink()

    def test_plugin_settings_precedence_order(
        self,
        session,
        tap,
        plugin_settings_service_factory,
        monkeypatch,
    ):
        """Test that plugin settings follow the correct precedence order."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".meltanorc", delete=False
        ) as temp_file:
            config_content = """plugins:
  extractors:
    tap-mock:
      test: "user-config-value"
      password: "user-config-password"
"""
            temp_file.write(config_content)
            temp_file.flush()

            try:
                # Patch the user config path to use our temporary file
                with patch.object(
                    YamlConfigLoader,
                    "_get_user_config_path",
                    return_value=Path(temp_file.name),
                ):
                    # Create PluginSettingsService using the fixture
                    settings_service = plugin_settings_service_factory(tap)

                    # Test that user config is used when no higher precedence source
                    assert settings_service.get("test") == "user-config-value"

                    # Test that environment variables override user config
                    monkeypatch.setenv("TAP_MOCK_TEST", "env-value")
                    assert settings_service.get("test") == "env-value"
                    # But password should still come from user config
                    assert settings_service.get("password") == "user-config-password"

            finally:
                Path(temp_file.name).unlink()

    def test_user_config_store_in_precedence_chain(self):
        """Test that USER_CONFIG store is correctly positioned in precedence chain."""
        stores = list(SettingValueStore)

        # Find the indices of relevant stores
        config_override_idx = stores.index(SettingValueStore.CONFIG_OVERRIDE)
        env_idx = stores.index(SettingValueStore.ENV)
        dotenv_idx = stores.index(SettingValueStore.DOTENV)
        user_config_idx = stores.index(SettingValueStore.USER_CONFIG)
        meltano_env_idx = stores.index(SettingValueStore.MELTANO_ENVIRONMENT)
        meltano_yml_idx = stores.index(SettingValueStore.MELTANO_YML)
        db_idx = stores.index(SettingValueStore.DB)
        inherited_idx = stores.index(SettingValueStore.INHERITED)
        default_idx = stores.index(SettingValueStore.DEFAULT)

        # Verify the correct precedence order
        assert config_override_idx < env_idx < dotenv_idx < user_config_idx
        assert user_config_idx < meltano_env_idx < meltano_yml_idx
        assert meltano_yml_idx < db_idx < inherited_idx < default_idx

        # Test that USER_CONFIG can override lower precedence stores
        assert SettingValueStore.USER_CONFIG.overrides(
            SettingValueStore.MELTANO_ENVIRONMENT
        )
        assert SettingValueStore.USER_CONFIG.overrides(SettingValueStore.MELTANO_YML)
        assert SettingValueStore.USER_CONFIG.overrides(SettingValueStore.DB)
        assert SettingValueStore.USER_CONFIG.overrides(SettingValueStore.INHERITED)
        assert SettingValueStore.USER_CONFIG.overrides(SettingValueStore.DEFAULT)

        # Test that higher precedence stores can override USER_CONFIG
        assert SettingValueStore.CONFIG_OVERRIDE.overrides(
            SettingValueStore.USER_CONFIG
        )
        assert SettingValueStore.ENV.overrides(SettingValueStore.USER_CONFIG)
        assert SettingValueStore.DOTENV.overrides(SettingValueStore.USER_CONFIG)

    def test_plugin_settings_with_source_attribution(
        self, session, tap, plugin_settings_service_factory
    ):
        """Test that plugin settings show correct source attribution."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".meltanorc", delete=False
        ) as temp_file:
            config_content = """plugins:
  extractors:
    tap-mock:
      test: "user-config-value"
"""
            temp_file.write(config_content)
            temp_file.flush()

            try:
                # Patch the user config path to use our temporary file
                with patch.object(
                    YamlConfigLoader,
                    "_get_user_config_path",
                    return_value=Path(temp_file.name),
                ):
                    # Create PluginSettingsService using the fixture
                    settings_service = plugin_settings_service_factory(tap)

                    # Test source attribution for user config
                    value, source = settings_service.get_with_source(
                        "test", session=session
                    )
                    assert value == "user-config-value"
                    assert source == SettingValueStore.USER_CONFIG

            finally:
                Path(temp_file.name).unlink()

    def test_plugin_settings_complex_values(
        self,
        session,
        tap,
        plugin_settings_service_factory,
    ):
        """Test plugin settings with complex configuration values."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".meltanorc", delete=False
        ) as temp_file:
            config_content = """plugins:
  extractors:
    tap-mock:
      test: "simple-value"
      test_list:
        - "item1"
        - "item2"
      test_dict:
        key1: "value1"
        key2: "value2"
"""
            temp_file.write(config_content)
            temp_file.flush()

            try:
                # Patch the user config path to use our temporary file
                with patch.object(
                    YamlConfigLoader,
                    "_get_user_config_path",
                    return_value=Path(temp_file.name),
                ):
                    # Create PluginSettingsService using the fixture
                    settings_service = plugin_settings_service_factory(tap)

                    # Test simple value
                    assert settings_service.get("test") == "simple-value"

                    # Test complex values (converted to strings)
                    test_list = settings_service.get("test_list")
                    assert "item1" in test_list
                    assert "item2" in test_list

                    test_dict = settings_service.get("test_dict")
                    assert "key1" in test_dict
                    assert "value1" in test_dict

            finally:
                Path(temp_file.name).unlink()
