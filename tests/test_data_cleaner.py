from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import unittest

from meltano.transformations.data_cleaner import CleanConfig, clean_data, validate_data


class TestDataCleaner(unittest.TestCase):
    def test_clean_data(self):
        records = [
            {"Name": "Alice", "Age": 25, "City": None},
            {"Name": "Bob", "Age": None, "City": "New York"},
        ]
        cleaned = clean_data(records)
        expected = [{"name": "Alice", "age": 25}, {"name": "Bob", "city": "New York"}]
        self.assertEqual(cleaned, expected)

    def test_clean_data_empty_input(self):
        # Edge case: empty input
        records = []
        cleaned = clean_data(records)
        expected = []
        self.assertEqual(cleaned, expected)

    def test_clean_data_all_none(self):
        # Edge case: all None values
        records = [{"Name": None, "Age": None, "City": None}]
        cleaned = clean_data(records)
        expected = [{}]  # Empty dict
        self.assertEqual(cleaned, expected)

    def test_validate_data_success(self):
        records = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
        config = CleanConfig(required_fields=["name", "age"])
        self.assertTrue(validate_data(records, config))

    def test_validate_data_failure(self):
        records = [{"name": "Alice"}, {"name": "Bob", "age": 30}]
        config = CleanConfig(required_fields=["name", "age"])
        self.assertFalse(validate_data(records, config))


if __name__ == "__main__":
    unittest.main()
