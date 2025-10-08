"""Integration tests for log parsing functionality."""

from __future__ import annotations

import pytest

from meltano.core.logging.output_logger import OutputLogger
from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.project import Project


class TestLogParsingIntegration:
    """Integration tests for log parsing functionality."""

    @pytest.fixture
    def project(self, tmp_path):
        """Create a test project."""
        meltano_yml = tmp_path / "meltano.yml"
        meltano_yml.write_text("version: 1\ndefault_environment: dev\n")
        return Project(tmp_path)

    def create_invoker(self, project, plugin, log_parser_config=None):
        """Helper to create a PluginInvoker with log parser config."""
        invoker = PluginInvoker(project, plugin)
        if log_parser_config is not None:
            invoker.plugin_config_extras = {"_log_parser": log_parser_config}
        else:
            invoker.plugin_config_extras = {}
        return invoker

    @pytest.fixture
    def plugin_with_singer_sdk_parser(self):
        """Create a plugin configured with singer-sdk log parser."""
        return ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="test-tap",
            namespace="test_tap",
            pip_url="test-tap",
            capabilities=["structured-logging", "catalog", "discover"],
        )

    @pytest.fixture
    def plugin_with_default_parser(self):
        """Create a plugin configured with default log parser."""
        return ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="test-tap-default",
            namespace="test_tap_default",
            pip_url="test-tap-default",
            capabilities=["structured-logging", "catalog", "discover"],
        )

    @pytest.fixture
    def plugin_without_structured_logging(self):
        """Create a plugin without structured-logging capability."""
        return ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="test-tap-no-logging",
            namespace="test_tap_no_logging",
            pip_url="test-tap-no-logging",
            capabilities=["catalog", "discover"],
        )

    def test_singer_sdk_log_parser_integration(
        self,
        project,
        plugin_with_singer_sdk_parser,
        tmp_path,
    ):
        """Test that singer-sdk log parser is used when configured."""
        log_file = tmp_path / "test.log"
        output_logger = OutputLogger(file=log_file)

        # Test that the log parser is correctly retrieved from plugin invoker
        invoker = self.create_invoker(
            project, plugin_with_singer_sdk_parser, "singer-sdk"
        )
        log_parser = invoker.get_log_parser()
        assert log_parser == "singer-sdk"

        # Test that the Out object is created with correct log parser
        out = output_logger.out(
            name="test-tap",
            log_parser=log_parser,
        )

        assert out.log_parser == "singer-sdk"

    def test_default_log_parser_integration(
        self,
        project,
        plugin_with_default_parser,
        tmp_path,
    ):
        """Test that default log parser is used when configured."""
        log_file = tmp_path / "test.log"
        output_logger = OutputLogger(file=log_file)

        invoker = self.create_invoker(project, plugin_with_default_parser, "default")
        log_parser = invoker.get_log_parser()
        assert log_parser == "default"

        out = output_logger.out(
            name="test-tap-default",
            log_parser=log_parser,
        )

        assert out.log_parser == "default"

    def test_no_log_parser_when_no_structured_logging(
        self,
        project,
        plugin_without_structured_logging,
        tmp_path,
    ):
        """Test no log parser when structured-logging capability is absent."""
        log_file = tmp_path / "test.log"
        output_logger = OutputLogger(file=log_file)

        invoker = self.create_invoker(
            project, plugin_without_structured_logging, "singer-sdk"
        )
        log_parser = invoker.get_log_parser()
        assert log_parser is None

        out = output_logger.out(
            name="test-tap-no-logging",
            log_parser=log_parser,
        )

        assert out.log_parser is None

    def test_parser_factory_integration(
        self,
        project,
        plugin_with_singer_sdk_parser,
        tmp_path,
    ):
        """Test that log parser is correctly integrated with output logger."""
        log_file = tmp_path / "test.log"
        output_logger = OutputLogger(file=log_file)

        invoker = self.create_invoker(
            project, plugin_with_singer_sdk_parser, "singer-sdk"
        )
        log_parser = invoker.get_log_parser()
        out = output_logger.out(
            name="test-tap",
            log_parser=log_parser,
        )

        # Verify that the correct log parser is configured
        assert out.log_parser == "singer-sdk"

    def test_structured_logging_capability_detection(self, project):
        """Test that structured-logging capability is correctly detected."""
        # Plugin with structured-logging capability
        plugin_with = ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="test-with-logging",
            namespace="test_with_logging",
            pip_url="test-with-logging",
            capabilities=["structured-logging", "catalog"],
        )

        # Plugin without structured-logging capability
        plugin_without = ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="test-without-logging",
            namespace="test_without_logging",
            pip_url="test-without-logging",
            capabilities=["catalog"],
        )

        assert "structured-logging" in plugin_with.capabilities
        invoker_with = self.create_invoker(project, plugin_with, "singer-sdk")
        assert invoker_with.get_log_parser() == "singer-sdk"

        assert "structured-logging" not in plugin_without.capabilities
        invoker_without = self.create_invoker(project, plugin_without, "singer-sdk")
        assert (
            invoker_without.get_log_parser() is None
        )  # Should return None despite config

    @pytest.mark.parametrize(
        ("capabilities", "parser_config", "expected_parser"),
        (
            (["structured-logging"], "singer-sdk", "singer-sdk"),
            (["structured-logging"], "default", "default"),
            (["structured-logging"], None, None),  # No parser when no config
            (["catalog"], "singer-sdk", None),  # No structured-logging capability
            ([], "singer-sdk", None),  # No capabilities at all
        ),
    )
    def test_log_parser_combinations(
        self, project, capabilities, parser_config, expected_parser
    ):
        """Test various combinations of capabilities and parser configurations."""
        plugin = ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="test-plugin",
            namespace="test_plugin",
            pip_url="test-plugin",
            capabilities=capabilities,
        )

        invoker = self.create_invoker(project, plugin, parser_config)
        log_parser = invoker.get_log_parser()
        assert log_parser == expected_parser
