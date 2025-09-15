"""Integration tests for log parsing functionality."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from meltano.core.logging.output_logger import OutputLogger
from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin


class TestLogParsingIntegration:
    """Integration tests for log parsing functionality."""

    @pytest.fixture
    def plugin_with_singer_sdk_parser(self):
        """Create a plugin configured with singer-sdk log parser."""
        return ProjectPlugin(
            name="test-tap",
            namespace="test_tap",
            pip_url="test-tap",
            plugin_type=PluginType.EXTRACTORS,
            extra_config={"_log_parser": "singer-sdk"},
            definition={
                "capabilities": ["structured-logging", "catalog", "discover"],
            },
        )

    @pytest.fixture
    def plugin_with_default_parser(self):
        """Create a plugin configured with default log parser."""
        return ProjectPlugin(
            name="test-tap-default",
            namespace="test_tap_default",
            pip_url="test-tap-default",
            plugin_type=PluginType.EXTRACTORS,
            extra_config={"_log_parser": "default"},
            definition={
                "capabilities": ["structured-logging", "catalog", "discover"],
            },
        )

    @pytest.fixture
    def plugin_without_structured_logging(self):
        """Create a plugin without structured-logging capability."""
        return ProjectPlugin(
            name="test-tap-no-logging",
            namespace="test_tap_no_logging",
            pip_url="test-tap-no-logging",
            plugin_type=PluginType.EXTRACTORS,
            definition={
                "capabilities": ["catalog", "discover"],
            },
        )

    def test_singer_sdk_log_parser_integration(
        self,
        plugin_with_singer_sdk_parser,
        tmp_path,
    ):
        """Test that singer-sdk log parser is used when configured."""
        log_file = tmp_path / "test.log"
        output_logger = OutputLogger(file=log_file)

        # Test that the log parser is correctly retrieved from plugin
        log_parser = plugin_with_singer_sdk_parser.get_log_parser()
        assert log_parser == "singer-sdk"

        # Test that the Out object is created with correct log parser
        out = output_logger.out(
            name="test-tap",
            log_parser=log_parser,
        )

        assert out.log_parser == "singer-sdk"

    def test_default_log_parser_integration(
        self,
        plugin_with_default_parser,
        tmp_path,
    ):
        """Test that default log parser is used when configured."""
        log_file = tmp_path / "test.log"
        output_logger = OutputLogger(file=log_file)

        log_parser = plugin_with_default_parser.get_log_parser()
        assert log_parser == "default"

        out = output_logger.out(
            name="test-tap-default",
            log_parser=log_parser,
        )

        assert out.log_parser == "default"

    def test_no_log_parser_when_no_structured_logging(
        self,
        plugin_without_structured_logging,
        tmp_path,
    ):
        """Test that no log parser is used when structured-logging capability is absent."""
        log_file = tmp_path / "test.log"
        output_logger = OutputLogger(file=log_file)

        log_parser = plugin_without_structured_logging.get_log_parser()
        assert log_parser is None

        out = output_logger.out(
            name="test-tap-no-logging",
            log_parser=log_parser,
        )

        assert out.log_parser is None

    @patch("meltano.core.logging.parsers.get_parser_factory")
    def test_parser_factory_called_with_correct_parser(
        self,
        mock_get_parser_factory,
        plugin_with_singer_sdk_parser,
        tmp_path,
    ):
        """Test that the parser factory is called with the correct log parser."""
        log_file = tmp_path / "test.log"
        output_logger = OutputLogger(file=log_file)

        # Mock parser factory
        mock_parser = MagicMock()
        mock_get_parser_factory.return_value = mock_parser

        log_parser = plugin_with_singer_sdk_parser.get_log_parser()
        out = output_logger.out(
            name="test-tap",
            log_parser=log_parser,
        )

        # Verify parser factory was called with singer-sdk
        mock_get_parser_factory.assert_called_with("singer-sdk")

    def test_structured_logging_capability_detection(self):
        """Test that structured-logging capability is correctly detected."""
        # Plugin with structured-logging capability
        plugin_with = ProjectPlugin(
            name="test-with-logging",
            namespace="test_with_logging",
            pip_url="test-with-logging",
            plugin_type=PluginType.EXTRACTORS,
            extra_config={"_log_parser": "singer-sdk"},
            definition={
                "capabilities": ["structured-logging", "catalog"],
            },
        )

        # Plugin without structured-logging capability
        plugin_without = ProjectPlugin(
            name="test-without-logging",
            namespace="test_without_logging",
            pip_url="test-without-logging",
            plugin_type=PluginType.EXTRACTORS,
            extra_config={
                "_log_parser": "singer-sdk"
            },  # Config present but capability missing
            definition={
                "capabilities": ["catalog"],
            },
        )

        assert "structured-logging" in plugin_with.capabilities
        assert plugin_with.get_log_parser() == "singer-sdk"

        assert "structured-logging" not in plugin_without.capabilities
        assert (
            plugin_without.get_log_parser() is None
        )  # Should return None despite config

    @pytest.mark.parametrize(
        "capabilities,parser_config,expected_parser",
        [
            (["structured-logging"], "singer-sdk", "singer-sdk"),
            (["structured-logging"], "default", "default"),
            (["structured-logging"], None, "singer-sdk"),  # Default to singer-sdk
            (["catalog"], "singer-sdk", None),  # No structured-logging capability
            ([], "singer-sdk", None),  # No capabilities at all
        ],
    )
    def test_log_parser_combinations(
        self, capabilities, parser_config, expected_parser
    ):
        """Test various combinations of capabilities and parser configurations."""
        extra_config = {"_log_parser": parser_config} if parser_config else {}
        plugin = ProjectPlugin(
            name="test-plugin",
            namespace="test_plugin",
            pip_url="test-plugin",
            plugin_type=PluginType.EXTRACTORS,
            extra_config=extra_config,
            definition={
                "capabilities": capabilities,
            },
        )

        log_parser = plugin.get_log_parser()
        assert log_parser == expected_parser
