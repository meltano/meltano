"""Tests for UserConfigStoreManager integration."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from meltano.core.plugin.base import PluginType
from meltano.core.settings_store import SettingValueStore, UserConfigStoreManager
from meltano.core.yaml_config import YamlConfigLoader


class TestUserConfigStoreManagerIntegration:
    """Test UserConfigStoreManager integration with plugin settings."""

    def test_user_config_store_manager_creation(self):
        """Test that UserConfigStoreManager can be created."""
        # Test that the enum includes USER_CONFIG
        assert hasattr(SettingValueStore, "USER_CONFIG")

        # Test that USER_CONFIG has a manager mapping
        user_config_store = SettingValueStore.USER_CONFIG
        assert user_config_store.manager == UserConfigStoreManager

        # Test that it's in the correct precedence order
        stores_list = list(SettingValueStore)
        user_config_index = stores_list.index(SettingValueStore.USER_CONFIG)
        dotenv_index = stores_list.index(SettingValueStore.DOTENV)
        meltano_env_index = stores_list.index(SettingValueStore.MELTANO_ENVIRONMENT)

        # USER_CONFIG should be after DOTENV but before MELTANO_ENVIRONMENT
        assert dotenv_index < user_config_index < meltano_env_index

    def test_user_config_store_manager_plugin_settings(self):
        """Test that UserConfigStoreManager can read plugin settings."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".meltanorc", delete=False
        ) as temp_file:
            config_content = """plugins:
  extractors:
    tap-github:
      token: "test-token"
      repository: "test/repo"
  loaders:
    target-postgres:
      host: "localhost"
      port: 5432
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
                    # Create mock plugin and settings service
                    mock_plugin = Mock()
                    mock_plugin.type = PluginType.EXTRACTORS
                    mock_plugin.name = "tap-github"

                    mock_settings_service = Mock()
                    mock_settings_service.plugin = mock_plugin
                    mock_settings_service.project = Mock()

                    # Create UserConfigStoreManager instance
                    store_manager = UserConfigStoreManager(mock_settings_service)

                    # Test getting existing setting
                    value, metadata = store_manager.get("token")
                    assert value == "test-token"
                    assert "user config for extractors.tap-github" in metadata["source"]

                    # Test getting non-existent setting
                    value, metadata = store_manager.get("non_existent")
                    assert value is None
                    assert metadata == {}

            finally:
                Path(temp_file.name).unlink()

    def test_user_config_store_manager_no_plugin(self):
        """Test UserConfigStoreManager with non-plugin settings service."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".meltanorc", delete=False
        ) as temp_file:
            config_content = """meltano:
  yaml_width: 100
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
                    # Create mock non-plugin settings service (project settings)
                    mock_settings_service = Mock()
                    # Remove plugin attribute to simulate ProjectSettingsService
                    del mock_settings_service.plugin
                    mock_settings_service.project = Mock()

                    # Create UserConfigStoreManager instance
                    store_manager = UserConfigStoreManager(mock_settings_service)

                    # Test getting setting when no plugin context
                    value, metadata = store_manager.get("yaml_width")
                    assert (
                        value is None
                    )  # Should not find project settings in user config
                    assert metadata == {}

            finally:
                Path(temp_file.name).unlink()

    def test_user_config_store_manager_different_plugin_types(self):
        """Test UserConfigStoreManager with different plugin types."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".meltanorc", delete=False
        ) as temp_file:
            config_content = """plugins:
  extractors:
    tap-github:
      token: "github-token"
  loaders:
    target-postgres:
      host: "localhost"
  transformers:
    dbt:
      profiles_dir: "/path/to/profiles"
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
                    # Test extractor
                    mock_extractor = Mock()
                    mock_extractor.type = PluginType.EXTRACTORS
                    mock_extractor.name = "tap-github"

                    mock_settings_service = Mock()
                    mock_settings_service.plugin = mock_extractor
                    mock_settings_service.project = Mock()

                    store_manager = UserConfigStoreManager(mock_settings_service)
                    value, metadata = store_manager.get("token")
                    assert value == "github-token"

                    # Test loader
                    mock_loader = Mock()
                    mock_loader.type = PluginType.LOADERS
                    mock_loader.name = "target-postgres"

                    mock_settings_service.plugin = mock_loader
                    store_manager = UserConfigStoreManager(mock_settings_service)
                    value, metadata = store_manager.get("host")
                    assert value == "localhost"

                    # Test transformer
                    mock_transformer = Mock()
                    mock_transformer.type = PluginType.TRANSFORMERS
                    mock_transformer.name = "dbt"

                    mock_settings_service.plugin = mock_transformer
                    store_manager = UserConfigStoreManager(mock_settings_service)
                    value, metadata = store_manager.get("profiles_dir")
                    assert value == "/path/to/profiles"

            finally:
                Path(temp_file.name).unlink()

    def test_user_config_store_manager_write_operations_not_supported(self):
        """Test that write operations are not yet supported."""
        mock_settings_service = Mock()
        mock_settings_service.project = Mock()

        store_manager = UserConfigStoreManager(mock_settings_service)

        # Test that write operations raise StoreNotSupportedError
        from meltano.core.settings_store import StoreNotSupportedError

        with pytest.raises(
            StoreNotSupportedError, match="does not yet support 'set' operations"
        ):
            store_manager.set("key", "value")

        with pytest.raises(
            StoreNotSupportedError, match="does not yet support 'unset' operations"
        ):
            store_manager.unset("key", ["key"])

        with pytest.raises(
            StoreNotSupportedError, match="does not yet support 'reset' operations"
        ):
            store_manager.reset()

    def test_user_config_store_manager_complex_values(self):
        """Test UserConfigStoreManager with complex configuration values."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".meltanorc", delete=False
        ) as temp_file:
            config_content = """plugins:
  extractors:
    tap-csv:
      files:
        - "data1.csv"
        - "data2.csv"
      config:
        delimiter: ","
        quote_char: '"'
      port: 5432
      enabled: true
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
                    # Create mock plugin and settings service
                    mock_plugin = Mock()
                    mock_plugin.type = PluginType.EXTRACTORS
                    mock_plugin.name = "tap-csv"

                    mock_settings_service = Mock()
                    mock_settings_service.plugin = mock_plugin
                    mock_settings_service.project = Mock()

                    # Create UserConfigStoreManager instance
                    store_manager = UserConfigStoreManager(mock_settings_service)

                    # Test getting list value
                    value, metadata = store_manager.get("files")
                    assert value == "['data1.csv', 'data2.csv']"

                    # Test getting nested dict value
                    value, metadata = store_manager.get("config")
                    assert "delimiter" in str(value)
                    assert "quote_char" in str(value)

                    # Test getting integer value
                    value, metadata = store_manager.get("port")
                    assert value == "5432"

                    # Test getting boolean value
                    value, metadata = store_manager.get("enabled")
                    assert value == "True"

            finally:
                Path(temp_file.name).unlink()
