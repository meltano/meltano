"""Tests for user configuration service."""

from __future__ import annotations

import tempfile
import threading
import time
from contextlib import contextmanager, suppress
from pathlib import Path

import pytest

from meltano.core.user_config import (
    UserConfigReadError,
    UserConfigService,
    YamlSettings,
    _reset_user_config_service,
    get_user_config_service,
)


class TestUserConfigService:
    """Test UserConfigService class."""

    def teardown_method(self):
        _reset_user_config_service()

    @contextmanager
    def _config_file(self, content: str | None = None):
        if content is None:
            with tempfile.TemporaryDirectory() as tmpdir:
                yield Path(tmpdir) / "nonexistent.yml"
        else:
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".yml"
            ) as tmp:
                tmp.write(content)
                tmp.flush()
                config_path = Path(tmp.name)
                try:
                    yield config_path
                finally:
                    with suppress(PermissionError):
                        config_path.unlink()

    def test_default_config(self):
        with self._config_file() as config_path:
            assert UserConfigService(config_path).yaml.indent == 2

    def test_read_yaml_indent(self):
        with self._config_file("yaml:\n  indent: 4\n") as config_path:
            assert UserConfigService(config_path).yaml.indent == 4

    def test_invalid_yaml_indent(self):
        with (
            self._config_file("yaml:\n  indent: not_a_number\n") as config_path,
            pytest.raises(ValueError, match="invalid literal for int"),
        ):
            _ = UserConfigService(config_path).yaml.indent

    def test_missing_yaml_section(self):
        with self._config_file("other:\n  setting: value\n") as config_path:
            assert UserConfigService(config_path).yaml.indent == 2

    def test_get_user_config_service_singleton(self):
        config1 = get_user_config_service()
        config2 = get_user_config_service()
        assert config1 is config2

    def test_get_user_config_service_with_path(self):
        with self._config_file("yaml:\n  indent: 8\n") as config_path:
            user_config_service = get_user_config_service(config_path)
            assert user_config_service.yaml.indent == 8
            assert user_config_service.config_path == config_path

    @pytest.mark.parametrize(
        ("content", "config"),
        (
            pytest.param(
                "yaml:\n  indent: 4\n",
                YamlSettings(_indent=4),
                id="indent",
            ),
            pytest.param(
                "yaml:\n  block_seq_indent: 2\n",
                YamlSettings(_block_seq_indent=2),
                id="block_seq_indent",
            ),
            pytest.param(
                "yaml:\n  sequence_dash_offset: 3\n",
                YamlSettings(_sequence_dash_offset=3),
                id="sequence_dash_offset",
            ),
        ),
    )
    def test_yaml_settings(self, content: str, config: YamlSettings):
        with self._config_file(content) as config_path:
            settings = UserConfigService(config_path).yaml
            assert settings == config

    def test_yaml_settings_empty(self):
        with self._config_file("other:\n  key: value\n") as config_path:
            _ = UserConfigService(config_path).yaml

    def test_config_read_error(self):
        """Test UserConfigReadError is raised for invalid config files."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yml") as tmp:
            tmp.write("invalid: yaml: content: [\n    - unclosed")
            tmp.flush()
            config_path = Path(tmp.name)

            service = UserConfigService(config_path)
            try:
                with pytest.raises(UserConfigReadError) as exc_info:
                    _ = service.config
                assert isinstance(exc_info.value, UserConfigReadError)
                assert exc_info.value.config_path == config_path
                assert exc_info.value.original_error is not None
            finally:
                with suppress(PermissionError):
                    config_path.unlink()

    def test_yaml_settings_validation(self):
        """Test validation of YAML settings."""
        config = """yaml:
  indent: -1
  block_seq_indent: -5
"""
        with self._config_file(config) as config_path:
            service = UserConfigService(config_path)

            # Should use defaults for invalid values
            assert service.yaml.indent == 2
            assert service.yaml.block_seq_indent == 0

    def test_threading_safety(self):
        """Test thread-safe singleton access."""
        results = []

        def create_service():
            # Add small delay to increase chance of race condition
            time.sleep(0.01)
            service = get_user_config_service()
            results.append(service)

        threads = [threading.Thread(target=create_service) for _ in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        assert len({id(service) for service in results}) == 1

    def test_get_user_config_service_with_different_path(self):
        """Test that providing different config_path creates new instance."""
        service1 = get_user_config_service()

        with self._config_file("yaml:\n  indent: 4\n") as config_path:
            service2 = get_user_config_service(config_path)

            assert service1 is not service2
            assert service2.config_path == config_path

    def test_config_not_mapping(self):
        """Test config file where root is not a mapping."""
        with (
            self._config_file("- item1\n- item2\n") as config_path,
            pytest.raises(
                AttributeError,
                match="'list' object has no attribute 'get'",
            ),
        ):
            _ = UserConfigService(config_path).yaml

    def test_platformdirs_integration(self):
        """Test that UserConfigService uses platformdirs correctly."""
        from pathlib import Path

        import platformdirs

        service = UserConfigService()
        expected_dir = platformdirs.user_config_path("meltano")
        expected_path = Path(expected_dir) / "config.yml"

        assert service.config_path == expected_path
