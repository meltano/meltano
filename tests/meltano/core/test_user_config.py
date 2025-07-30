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
                yield Path(tmpdir) / "nonexistent.ini"
        else:
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".ini"
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
            assert UserConfigService(config_path).yaml_indent == 2

    def test_read_yaml_indent(self):
        with self._config_file("[yaml]\nindent = 4\n") as config_path:
            assert UserConfigService(config_path).yaml_indent == 4

    def test_invalid_yaml_indent(self):
        with self._config_file("[yaml]\nindent = not_a_number\n") as config_path:
            assert UserConfigService(config_path).yaml_indent == 2

    def test_missing_yaml_section(self):
        with self._config_file("[other]\nsetting = value\n") as config_path:
            assert UserConfigService(config_path).yaml_indent == 2

    def test_get_user_config_service_singleton(self):
        config1 = get_user_config_service()
        config2 = get_user_config_service()
        assert config1 is config2

    def test_get_user_config_service_with_path(self):
        with self._config_file("[yaml]\nindent = 8\n") as config_path:
            user_config_service = get_user_config_service(config_path)
            assert user_config_service.yaml_indent == 8
            assert user_config_service.config_path == config_path

    def test_yaml_settings_all_types(self):
        config = """[yaml]
indent = 4
width = 120
preserve_quotes = true
explicit_start = yes
explicit_end = false
allow_unicode = no
default_flow_style = 1
line_break = \\n
encoding = utf-8
map_indent = none
"""
        with self._config_file(config) as config_path:
            settings = UserConfigService(config_path).yaml_settings()
            assert settings["indent"] == 4
            assert settings["width"] == 120
            assert settings["preserve_quotes"] is True
            assert settings["explicit_start"] is True
            assert settings["explicit_end"] is False
            assert settings["allow_unicode"] is False
            assert settings["default_flow_style"] is True
            assert settings["line_break"] == "\\n"
            assert settings["encoding"] == "utf-8"
            assert settings["map_indent"] is None

    def test_yaml_settings_empty(self):
        with self._config_file("[other]\nkey = value\n") as config_path:
            assert UserConfigService(config_path).yaml_settings() == {}

    def test_config_read_error(self):
        """Test UserConfigReadError is raised for invalid config files."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".ini") as tmp:
            tmp.write("invalid ini content\nwithout proper format")
            tmp.flush()
            config_path = Path(tmp.name)

            service = UserConfigService(config_path)
            try:
                with pytest.raises(UserConfigReadError) as exc_info:
                    _ = service.config
                assert exc_info.value.config_path == config_path
                assert exc_info.value.original_error is not None
            finally:
                with suppress(PermissionError):
                    config_path.unlink()

    def test_yaml_settings_validation(self):
        """Test validation of YAML settings."""
        config = """[yaml]
indent = -1
width = 0
block_seq_indent = -5
"""
        with self._config_file(config) as config_path:
            service = UserConfigService(config_path)
            settings = service.yaml_settings()

            # Should use defaults for invalid values
            assert settings["indent"] == 2
            assert settings["width"] == 80
            assert settings["block_seq_indent"] == 0

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

        with self._config_file("[yaml]\nindent = 4\n") as config_path:
            service2 = get_user_config_service(config_path)

            assert service1 is not service2
            assert service2.config_path == config_path

    def test_parse_value_edge_cases(self):
        """Test _parse_value method with various edge cases."""
        with self._config_file("[yaml]\ntest = value\n") as config_path:
            service = UserConfigService(config_path)
            
            # Test None values
            assert service._parse_value("none") is None
            assert service._parse_value("null") is None
            assert service._parse_value("") is None
            assert service._parse_value("NONE") is None  # Case insensitive
            
            # Test boolean values
            assert service._parse_value("true") is True
            assert service._parse_value("false") is False
            assert service._parse_value("1") is True
            assert service._parse_value("0") is False
            
            # Test integer values
            assert service._parse_value("123") == 123
            assert service._parse_value("-456") == -456
            
            # Test string values (fallback)
            assert service._parse_value("not_a_bool_or_int") == "not_a_bool_or_int"
            assert service._parse_value("12.34") == "12.34"  # Float strings remain strings
