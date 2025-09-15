"""Tests for plugin log parser functionality."""

from __future__ import annotations

import pytest

from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin


class TestPluginLogParser:
    """Test plugin log parser functionality."""

    @pytest.fixture
    def plugin_with_structured_logging(self):
        """Create a plugin with structured-logging capability."""
        return ProjectPlugin(
            name="test-plugin",
            namespace="test_plugin",
            pip_url="test-plugin",
            plugin_type=PluginType.EXTRACTORS,
            extra_config={"_log_parser": "singer-sdk"},
            definition={
                "capabilities": ["structured-logging", "catalog", "discover"],
            },
        )

    @pytest.fixture
    def plugin_without_structured_logging(self):
        """Create a plugin without structured-logging capability."""
        return ProjectPlugin(
            name="test-plugin-no-logging",
            namespace="test_plugin_no_logging",
            pip_url="test-plugin-no-logging",
            plugin_type=PluginType.EXTRACTORS,
            extra_config={"_log_parser": "singer-sdk"},
            definition={
                "capabilities": ["catalog", "discover"],
            },
        )

    @pytest.fixture
    def plugin_no_log_parser_config(self):
        """Create a plugin with structured-logging but no log parser config."""
        return ProjectPlugin(
            name="test-plugin-no-config",
            namespace="test_plugin_no_config",
            pip_url="test-plugin-no-config",
            plugin_type=PluginType.EXTRACTORS,
            definition={
                "capabilities": ["structured-logging", "catalog", "discover"],
            },
        )

    def test_get_log_parser_with_structured_logging_capability(
        self,
        plugin_with_structured_logging,
    ):
        """Test that get_log_parser returns the configured parser when structured-logging capability is present."""
        log_parser = plugin_with_structured_logging.get_log_parser()
        assert log_parser == "singer-sdk"

    def test_get_log_parser_without_structured_logging_capability(
        self,
        plugin_without_structured_logging,
    ):
        """Test that get_log_parser returns None when structured-logging capability is absent."""
        log_parser = plugin_without_structured_logging.get_log_parser()
        assert log_parser is None

    def test_get_log_parser_with_structured_logging_but_no_config(
        self,
        plugin_no_log_parser_config,
    ):
        """Test that get_log_parser returns 'singer-sdk' by default when structured-logging capability is present but no parser is configured."""
        log_parser = plugin_no_log_parser_config.get_log_parser()
        assert log_parser == "singer-sdk"

    @pytest.mark.parametrize(
        "parser_value,expected",
        [
            ("singer-sdk", "singer-sdk"),
            ("default", "default"),
            ("custom-parser", "custom-parser"),
            (None, "singer-sdk"),  # Default to singer-sdk when no config
        ],
    )
    def test_get_log_parser_different_values(self, parser_value, expected):
        """Test get_log_parser with different parser values."""
        extra_config = {"_log_parser": parser_value} if parser_value else {}
        plugin = ProjectPlugin(
            name="test-plugin",
            namespace="test_plugin",
            pip_url="test-plugin",
            plugin_type=PluginType.EXTRACTORS,
            extra_config=extra_config,
            definition={
                "capabilities": ["structured-logging"],
            },
        )

        log_parser = plugin.get_log_parser()
        assert log_parser == expected

    def test_opt_out_of_singer_sdk_parser(self):
        """Test that plugins can opt out of singer-sdk parser by explicitly setting a different parser."""
        # Plugin that explicitly opts out to use default parser
        plugin_opt_out = ProjectPlugin(
            name="test-plugin-opt-out",
            namespace="test_plugin_opt_out",
            pip_url="test-plugin-opt-out",
            plugin_type=PluginType.EXTRACTORS,
            extra_config={"_log_parser": "default"},
            definition={
                "capabilities": ["structured-logging"],
            },
        )

        log_parser = plugin_opt_out.get_log_parser()
        assert log_parser == "default"

    def test_default_singer_sdk_behavior(self):
        """Test that plugins with structured-logging capability default to singer-sdk parser."""
        # Plugin with structured-logging capability but no explicit log parser config
        plugin_default = ProjectPlugin(
            name="test-plugin-default",
            namespace="test_plugin_default",
            pip_url="test-plugin-default",
            plugin_type=PluginType.EXTRACTORS,
            definition={
                "capabilities": ["structured-logging", "catalog", "discover"],
            },
        )

        log_parser = plugin_default.get_log_parser()
        assert log_parser == "singer-sdk"
