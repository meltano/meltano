from __future__ import annotations

import io
import tempfile
from decimal import Decimal
from pathlib import Path

from ruamel.yaml import YAML, CommentedMap

from meltano.core import yaml
from meltano.core.yaml import _represent_decimal


def test_decimal_representation():
    """Test that Decimal values are properly represented in YAML."""
    data = CommentedMap()
    data["decimal_value"] = Decimal("123.45")
    data["regular_float"] = 67.89
    data["integer"] = 100

    # Test dumping to string
    stream = io.StringIO()
    yaml.dump(data, stream)
    output = stream.getvalue()

    # Verify decimal is represented as a float string
    assert "123.45" in output
    assert "67.89" in output
    assert "100" in output


def test_decimal_in_nested_structure():
    """Test that Decimal values work in nested YAML structures."""
    data = CommentedMap()
    data["config"] = CommentedMap()
    data["config"]["settings"] = CommentedMap()
    data["config"]["settings"]["price"] = Decimal("99.99")
    data["config"]["settings"]["discount"] = Decimal("0.15")
    data["other"] = {"nested": {"value": Decimal("42.0")}}

    stream = io.StringIO()
    yaml.dump(data, stream)
    output = stream.getvalue()

    assert "99.99" in output
    assert "0.15" in output
    assert "42.0" in output


def test_load_and_dump_with_decimals():
    """Test loading and dumping YAML files with decimal values."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
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
        f.write(yaml_content)
        temp_path = Path(f.name)

    try:
        # Load the YAML file
        loaded_data = yaml.load(temp_path)

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

    finally:
        temp_path.unlink()


def test_yaml_cache_with_decimals():
    """Test that YAML caching works correctly with decimal values."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        yaml_content = """
settings:
  decimal_setting: 123.45
"""
        f.write(yaml_content)
        temp_path = Path(f.name)

    try:
        # Load twice to test caching
        data1 = yaml.load(temp_path)
        data2 = yaml.load(temp_path)

        # Both should be the same object due to caching
        assert data1 is data2

        # Verify content
        assert "decimal_setting" in data1["settings"]
        assert data1["settings"]["decimal_setting"] == 123.45

    finally:
        temp_path.unlink()


def test_decimal_representer_function():
    """Test the _represent_decimal function directly."""
    yaml_instance = YAML()
    decimal_value = Decimal("123.456")

    # Test the representer function
    result = _represent_decimal(yaml_instance.representer, decimal_value)

    assert result.tag == "tag:yaml.org,2002:float"
    assert result.value == "123.456"


def test_mixed_numeric_types():
    """Test YAML handling with mixed numeric types including decimals."""
    data = CommentedMap()
    data["values"] = [
        Decimal("1.23"),
        4.56,
        789,
        Decimal("0.001"),
        float("inf"),
        Decimal("999999999.999999999"),
    ]

    stream = io.StringIO()
    yaml.dump(data, stream)
    output = stream.getvalue()

    # Verify all values are present in output
    assert "1.23" in output
    assert "4.56" in output
    assert "789" in output
    assert "0.001" in output
    assert "999999999.999999999" in output
