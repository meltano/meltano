from __future__ import annotations

import io
import typing as t
import uuid
from decimal import Decimal

from ruamel.yaml import YAML, CommentedMap

from meltano.core import yaml
from meltano.core.yaml import _represent_decimal

if t.TYPE_CHECKING:
    from pathlib import Path


def _create_test_data(**kwargs) -> CommentedMap:
    """Create a CommentedMap with test data."""
    data = CommentedMap()
    for key, value in kwargs.items():
        data[key] = value
    return data


def test_decimal_representation() -> None:
    """Test that Decimal values are properly represented in YAML."""
    data = _create_test_data(
        decimal_value=Decimal("123.45"), regular_float=67.89, integer=100
    )

    # Test dumping to string
    stream = io.StringIO()
    yaml.dump(data, stream)
    output = stream.getvalue()

    # Verify decimal is represented as a float string
    assert "123.45" in output
    assert "67.89" in output
    assert "100" in output


def test_decimal_in_nested_structure() -> None:
    """Test that Decimal values work in nested YAML structures."""
    config_settings = CommentedMap()
    config_settings["price"] = Decimal("99.99")
    config_settings["discount"] = Decimal("0.15")

    config = CommentedMap()
    config["settings"] = config_settings

    data = _create_test_data(
        config=config, other={"nested": {"value": Decimal("42.0")}}
    )

    stream = io.StringIO()
    yaml.dump(data, stream)
    output = stream.getvalue()

    assert "99.99" in output
    assert "0.15" in output
    assert "42.0" in output


def test_uuid_representation() -> None:
    """Test that UUID values are properly represented in YAML."""
    data = _create_test_data(uuid_value=uuid.uuid4())

    stream = io.StringIO()
    yaml.dump(data, stream)
    assert str(data["uuid_value"]) in stream.getvalue()


def test_load_and_dump_with_decimals(tmp_path: Path):
    """Test loading and dumping YAML files with decimal values."""
    yaml_content = """
config:
  settings:
    price: 123.45
    tax_rate: 0.08
    discount: 15.00
plugins:
  extractors:
    - name: tap-csv
      settings:
        batch_size: 1000.0
        timeout: 30.5
"""
    temp_file = tmp_path / "test.yml"
    temp_file.write_text(yaml_content)

    # Load the YAML file
    loaded_data = yaml.load(temp_file)

    # Modify with decimal values
    loaded_data["config"]["settings"]["price"] = Decimal("456.78")
    loaded_data["config"]["settings"]["new_decimal"] = Decimal("99.99")

    # Dump back to string
    stream = io.StringIO()
    yaml.dump(loaded_data, stream)
    output = stream.getvalue()

    # Verify decimal values are properly represented
    assert "456.78" in output
    assert "99.99" in output


def test_yaml_cache_with_decimals(tmp_path: Path):
    """Test that YAML caching works correctly with decimal values."""
    yaml_content = """
settings:
  decimal_setting: 123.45
"""
    temp_file = tmp_path / "test.yml"
    temp_file.write_text(yaml_content)

    # Load twice to test caching
    data1 = yaml.load(temp_file)
    data2 = yaml.load(temp_file)

    # Both should be the same object due to caching
    assert data1 is data2

    # Verify content
    assert "decimal_setting" in data1["settings"]
    assert data1["settings"]["decimal_setting"] == 123.45


def test_decimal_representer_function() -> None:
    """Test the _represent_decimal function directly."""
    yaml_instance = YAML()
    decimal_value = Decimal("123.456")

    # Test the representer function
    result = _represent_decimal(yaml_instance.representer, decimal_value)

    assert result.tag == "tag:yaml.org,2002:float"
    assert result.value == "123.456"


def test_mixed_numeric_types() -> None:
    """Test YAML handling with mixed numeric types including decimals."""
    data = _create_test_data(
        values=[
            Decimal("1.23"),
            4.56,
            789,
            Decimal("0.001"),
            float("inf"),
            Decimal("999999999.999999999"),
        ]
    )

    stream = io.StringIO()
    yaml.dump(data, stream)
    output = stream.getvalue()

    # Verify all values are present in output
    assert "1.23" in output
    assert "4.56" in output
    assert "789" in output
    assert "0.001" in output
    assert "999999999.999999999" in output


def test_yaml_width_prevents_line_wrapping() -> None:
    """Test that long lines are not wrapped due to sys.maxsize YAML width."""
    long_url = (
        "git+https://github.com/transferwise/pipelinewise-tap-mysql.git"
        "#subdirectory=singer-connectors/tap-mysql&ref=v1.2.3-with-very-long-branch-name"
        "&commit=abcdef1234567890abcdef1234567890abcdef12&parameter=very-long-parameter-value"
        "&another_param=another-very-long-parameter-value-to-test-extreme-lengths"
        "&more_params=additional-configuration-options-and-settings-for-comprehensive-testing"
    )

    data = CommentedMap(
        {
            "plugins": CommentedMap(
                {
                    "extractors": [
                        CommentedMap(
                            [
                                ("name", "tap-mysql"),
                                ("variant", "transferwise"),
                                ("pip_url", long_url),
                            ]
                        )
                    ]
                }
            )
        }
    )

    stream = io.StringIO()
    yaml.dump(data, stream)
    output = stream.getvalue()
    lines = output.strip().split("\n")

    pip_url_line = next((line for line in lines if "pip_url:" in line), None)

    assert pip_url_line is not None
    assert long_url in pip_url_line
    assert sum(1 for line in lines if long_url in line) == 1
