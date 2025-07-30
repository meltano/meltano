"""Test YAML module with user configuration."""

from __future__ import annotations

import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

from ruamel.yaml import CommentedMap

from meltano.core import yaml
from meltano.core.user_config import UserConfigService


class TestYAMLWithUserConfig:
    """Test YAML formatting with user configuration."""

    @contextmanager
    def _mock_user_config_service(self, config_path: Path):
        """Mock the user config service with the given config path."""
        with mock.patch(
            "meltano.core.yaml.get_user_config_service",
        ) as mock_get_config:
            mock_get_config.return_value = UserConfigService(config_path)
            yield

    def test_yaml_indent_from_user_config(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".ini") as tmp:
            tmp.write("[yaml]\nindent = 4\n")
            tmp.flush()
            config_path = Path(tmp.name)

            with self._mock_user_config_service(config_path):
                data = CommentedMap()
                data["project_id"] = "test"
                data["environments"] = [
                    {
                        "name": "dev",
                        "config": {"database": "dev_db", "host": "localhost"},
                    }
                ]

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

                out_path.unlink()

            config_path.unlink()

    def test_default_yaml_indent(self):
        with self._mock_user_config_service(Path("/nonexistent/.meltanorc")):
            data = CommentedMap()
            data["name"] = "test"
            data["items"] = ["a", "b", "c"]

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
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".ini") as tmp:
            tmp.write("[yaml]\nindent = 8\n")
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
                mock_get_config.return_value = UserConfigService(config_path)

                data = CommentedMap()
                data["name"] = "test"
                data["nested"] = {"key": "value"}

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

                out_path.unlink()

            config_path.unlink()

    def test_yaml_handles_config_read_error_gracefully(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".ini") as tmp:
            tmp.write("invalid ini content without sections")
            tmp.flush()
            config_path = Path(tmp.name)

            config_path.chmod(0o000)

            with self._mock_user_config_service(config_path):
                data = CommentedMap()
                data["name"] = "test"

                with tempfile.NamedTemporaryFile(
                    mode="w", delete=False, suffix=".yml"
                ) as out:
                    yaml.dump(data, out)
                    out_path = Path(out.name)

                output = out_path.read_text()
                assert output.strip() == "name: test"

                out_path.unlink()

            config_path.chmod(0o644)
            config_path.unlink()

    def test_yaml_instance_isolation(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".ini") as tmp:
            tmp.write("[yaml]\nindent = 6\nexplicit_start = true\n")
            tmp.flush()
            config_path = Path(tmp.name)

            with self._mock_user_config_service(config_path):
                data1 = CommentedMap()
                data1["test"] = "first"
                from io import StringIO

                output1 = StringIO()
                yaml.dump(data1, output1)
                result1 = output1.getvalue()

                data2 = CommentedMap()
                data2["test"] = "second"
                output2 = StringIO()
                yaml.dump(data2, output2)
                result2 = output2.getvalue()

                assert result1 == "---\ntest: first\n"
                assert result2 == "---\ntest: second\n"

            config_path.unlink()
