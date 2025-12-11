"""Tests for Python version compatibility utilities."""

from __future__ import annotations

import typing as t

import pytest

from meltano.core.utils.python_compatibility import (
    determine_plugin_python_version,
    get_current_python_version,
    is_python_version_supported,
)


class TestPythonCompatibility:
    """Test Python compatibility utility functions."""

    def test_get_current_python_version(self):
        """Test that current version is in correct format."""
        version = get_current_python_version()
        assert version.count(".") == 1
        parts = version.split(".")
        assert len(parts) == 2
        assert all(part.isdigit() for part in parts)

    def test_is_python_version_supported_no_restrictions(self):
        """Test that None/empty list means all versions supported."""
        assert is_python_version_supported(None, "3.11") is True
        assert is_python_version_supported([], "3.11") is True

    def test_is_python_version_supported_matches(self):
        """Test version matching."""
        assert is_python_version_supported(["3.10", "3.11"], "3.11") is True
        assert is_python_version_supported(["3.10", "3.11"], "3.12") is False

    def test_is_python_version_supported_default_current(self):
        """Test default current version detection."""
        current = get_current_python_version()
        assert is_python_version_supported([current]) is True

    @pytest.fixture
    def mock_variant_supported(self):
        """Mock variant with supported versions."""

        class MockVariant:
            supported_python_versions: t.ClassVar = ["3.10", "3.11", "3.12"]

        return MockVariant()

    @pytest.fixture
    def mock_variant_no_restrictions(self):
        """Mock variant without restrictions."""

        class MockVariant:
            supported_python_versions = None

        return MockVariant()

    @pytest.fixture
    def mock_variant_empty_list(self):
        """Mock variant with empty supported versions list."""

        class MockVariant:
            supported_python_versions: t.ClassVar = []

        return MockVariant()

    def test_determine_plugin_python_version_supported(
        self,
        mock_variant_supported,
    ):
        """Test when current version is supported."""
        version = determine_plugin_python_version(
            mock_variant_supported,
            current_version="3.11",
        )
        assert version is None

    def test_determine_plugin_python_version_not_supported(
        self,
        mock_variant_supported,
    ):
        """Test when current version is not supported."""
        version = determine_plugin_python_version(
            mock_variant_supported,
            current_version="3.9",
        )
        assert version == "python3.12"

    def test_determine_plugin_python_version_future_version(
        self,
        mock_variant_supported,
    ):
        """Test when current version is newer than supported."""
        version = determine_plugin_python_version(
            mock_variant_supported,
            current_version="3.13",
        )
        assert version == "python3.12"

    def test_determine_plugin_python_version_no_restrictions(
        self,
        mock_variant_no_restrictions,
    ):
        """Test when no restrictions exist."""
        version = determine_plugin_python_version(
            mock_variant_no_restrictions,
            current_version="3.8",
        )
        assert version is None

    def test_determine_plugin_python_version_empty_list(
        self,
        mock_variant_empty_list,
    ):
        """Test when supported versions is empty list."""
        version = determine_plugin_python_version(
            mock_variant_empty_list,
            current_version="3.11",
        )
        assert version is None

    def test_determine_plugin_python_version_default_current(
        self,
        mock_variant_supported,
    ):
        """Test that default current version is used when not specified."""
        current = get_current_python_version()
        # If running on supported version, should not auto-select
        if current in mock_variant_supported.supported_python_versions:
            version = determine_plugin_python_version(
                mock_variant_supported,
            )
            assert version is None
        else:
            # If running on unsupported version, should auto-select
            version = determine_plugin_python_version(
                mock_variant_supported,
            )
            assert version == "python3.12"
