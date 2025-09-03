"""Test YAML module with user configuration."""

from __future__ import annotations

import os
import tempfile
import uuid
from contextlib import contextmanager, suppress
from decimal import Decimal
from pathlib import Path
from unittest import mock

from ruamel.yaml import CommentedMap

from meltano.core import yaml
from meltano.core.user_config import UserConfigService, _reset_user_config_service


class TestYAMLWithUserConfig:
    """Test YAML formatting with user configuration."""

    def teardown_method(self):
        _reset_user_config_service()

    def _create_test_data(self, **kwargs) -> CommentedMap:
        """Create a CommentedMap with test data."""
        data = CommentedMap()
        for key, value in kwargs.items():
            data[key] = value
        return data

    def _setup_mock_config(self, mock_get_config, config_path: Path):
        """Setup mock configuration service."""
        mock_get_config.return_value = UserConfigService(config_path)

    @contextmanager
    def _mock_user_config_service(self, config_path: Path):
        """Mock the user config service with the given config path."""
        with (
            mock.patch.dict(os.environ, {"MELTANO_DISABLE_USER_YAML_CONFIG": "false"}),
            mock.patch(
                "meltano.core.yaml.get_user_config_service",
            ) as mock_get_config,
        ):
            self._setup_mock_config(mock_get_config, config_path)
            yield

    def test_yaml_indent_from_user_config(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yml") as tmp:
            tmp.write("yaml:\n  indent: 4\n")
            tmp.flush()
            config_path = Path(tmp.name)

            with self._mock_user_config_service(config_path):
                data = self._create_test_data(
                    project_id="test",
                    environments=[
                        {
                            "name": "dev",
                            "config": {"database": "dev_db", "host": "localhost"},
                        }
                    ],
                )

                with tempfile.NamedTemporaryFile(
                    mode="w", delete=False, suffix=".yml"
                ) as out:
                    yaml.dump(data, out)
                    out_path = Path(out.name)

                output = out_path.read_text()
                lines = output.strip().split("\n")

                assert lines[0] == "project_id: test"
                assert lines[1] == "environments:"
                assert lines[2] == "  - name: dev"
                assert lines[3] == "    config:"
                assert lines[4] == "        database: dev_db"
                assert lines[5] == "        host: localhost"

                with suppress(PermissionError):
                    out_path.unlink()

            with suppress(PermissionError):
                config_path.unlink()

    def test_default_yaml_indent(self):
        with self._mock_user_config_service(Path("/nonexistent/config.yml")):
            data = self._create_test_data(name="test", items=["a", "b", "c"])

            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".yml"
            ) as out:
                yaml.dump(data, out)
                out_path = Path(out.name)

            output = out_path.read_text()
            lines = output.strip().split("\n")

            assert lines[0] == "name: test"
            assert lines[1] == "items:"
            assert lines[2] == "- a"
            assert lines[3] == "- b"
            assert lines[4] == "- c"

            out_path.unlink()

    def test_environment_variable_disables_user_config(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yml") as tmp:
            tmp.write("yaml:\n  indent: 8\n")
            tmp.flush()
            config_path = Path(tmp.name)

            with (
                mock.patch.dict(
                    os.environ, {"MELTANO_DISABLE_USER_YAML_CONFIG": "true"}
                ),
                mock.patch(
                    "meltano.core.yaml.get_user_config_service",
                ) as mock_get_config,
            ):
                self._setup_mock_config(mock_get_config, config_path)

                data = self._create_test_data(name="test", nested={"key": "value"})

                with tempfile.NamedTemporaryFile(
                    mode="w", delete=False, suffix=".yml"
                ) as out:
                    yaml.dump(data, out)
                    out_path = Path(out.name)

                output = out_path.read_text()
                lines = output.strip().split("\n")

                assert lines[0] == "name: test"
                assert lines[1] == "nested:"
                assert lines[2] == "  key: value"

                with suppress(PermissionError):
                    out_path.unlink()

            with suppress(PermissionError):
                config_path.unlink()

    def test_yaml_handles_config_read_error_gracefully(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yml") as tmp:
            tmp.write("invalid yaml content:\n  - unclosed bracket [")
            tmp.flush()
            config_path = Path(tmp.name)

            config_path.chmod(0o000)

            with self._mock_user_config_service(config_path):
                data = self._create_test_data(name="test")

                with tempfile.NamedTemporaryFile(
                    mode="w", delete=False, suffix=".yml"
                ) as out:
                    yaml.dump(data, out)
                    out_path = Path(out.name)

                output = out_path.read_text()
                assert output.strip() == "name: test"

                with suppress(PermissionError):
                    out_path.unlink()

            config_path.chmod(0o644)
            with suppress(PermissionError):
                config_path.unlink()

    def test_yaml_decimal_and_uuid_types(self):
        """Test that Decimal and UUID types are properly represented in YAML."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yml") as tmp:
            tmp.write("yaml:\n  indent: 2\n")
            tmp.flush()
            config_path = Path(tmp.name)

            with self._mock_user_config_service(config_path):
                data = self._create_test_data(
                    decimal_value=Decimal("123.45"),
                    uuid_value=uuid.UUID("12345678-1234-5678-9012-123456789abc"),
                )

                from io import StringIO

                output = StringIO()
                yaml.dump(data, output)
                result = output.getvalue()

                assert "decimal_value: 123.45" in result
                assert "uuid_value: 12345678-1234-5678-9012-123456789abc" in result

            with suppress(PermissionError):
                config_path.unlink()

    def test_yaml_load_with_caching(self):
        """Test the yaml.load function with file caching."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yml") as tmp:
            tmp.write("test_key: test_value\nnested:\n  item: value\n")
            tmp.flush()
            yaml_path = Path(tmp.name)

            result = yaml.load(yaml_path)
            assert result["test_key"] == "test_value"
            assert result["nested"]["item"] == "value"

            # Test cache hit
            result2 = yaml.load(yaml_path)
            assert result2["test_key"] == "test_value"

            with suppress(PermissionError):
                yaml_path.unlink()

    def test_yaml_dump_returns_string_when_no_stream(self):
        """Test that yaml.dump() returns string when no stream provided."""
        with self._mock_user_config_service(Path("/nonexistent/config.yml")):
            data = self._create_test_data(name="test", value=123)

            # Test dump without stream (should return string)
            result = yaml.dump(data)

            assert isinstance(result, str)
            assert "name: test" in result
            assert "value: 123" in result

    def test_yaml_dump_with_stream_returns_none(self):
        """Test that yaml.dump() returns None when stream is provided."""
        with self._mock_user_config_service(Path("/nonexistent/config.yml")):
            data = self._create_test_data(name="test", value=456)

            from io import StringIO

            stream = StringIO()

            # Test dump with stream (should return None)
            result = yaml.dump(data, stream)

            assert result is None
            assert "name: test" in stream.getvalue()
            assert "value: 456" in stream.getvalue()
