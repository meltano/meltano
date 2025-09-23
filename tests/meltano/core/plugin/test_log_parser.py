"""Tests for plugin log parser functionality."""

from __future__ import annotations

import pytest

from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.project import Project


class TestPluginLogParser:
    """Test plugin log parser functionality."""

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
    def plugin_with_structured_logging(self):
        """Create a plugin with structured-logging capability."""
        return ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="test-plugin",
            namespace="test_plugin",
            pip_url="test-plugin",
            capabilities=["structured-logging", "catalog", "discover"],
        )

    @pytest.fixture
    def plugin_without_structured_logging(self):
        """Create a plugin without structured-logging capability."""
        return ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="test-plugin-no-logging",
            namespace="test_plugin_no_logging",
            pip_url="test-plugin-no-logging",
            capabilities=["catalog", "discover"],
        )

    @pytest.fixture
    def plugin_no_log_parser_config(self):
        """Create a plugin with structured-logging but no log parser config."""
        return ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="test-plugin-no-config",
            namespace="test_plugin_no_config",
            pip_url="test-plugin-no-config",
            capabilities=["structured-logging", "catalog", "discover"],
        )

    def test_get_log_parser_with_structured_logging_capability(
        self,
        project,
        plugin_with_structured_logging,
    ):
        """Test get_log_parser returns parser when structured-logging present."""
        invoker = self.create_invoker(
            project, plugin_with_structured_logging, "singer-sdk"
        )
        log_parser = invoker.get_log_parser()
        assert log_parser == "singer-sdk"

    def test_get_log_parser_without_structured_logging_capability(
        self,
        project,
        plugin_without_structured_logging,
    ):
        """Test get_log_parser returns None when structured-logging absent."""
        invoker = self.create_invoker(
            project, plugin_without_structured_logging, "singer-sdk"
        )
        log_parser = invoker.get_log_parser()
        assert log_parser is None

    def test_get_log_parser_with_structured_logging_but_no_config(
        self,
        project,
        plugin_no_log_parser_config,
    ):
        """Test get_log_parser returns None when no parser configured."""
        invoker = self.create_invoker(project, plugin_no_log_parser_config)
        log_parser = invoker.get_log_parser()
        assert log_parser is None

    @pytest.mark.parametrize(
        ("parser_value", "expected"),
        (
            ("singer-sdk", "singer-sdk"),
            ("default", "default"),
            ("custom-parser", "custom-parser"),
            (None, None),  # No parser when no config
        ),
    )
    def test_get_log_parser_different_values(self, project, parser_value, expected):
        """Test get_log_parser with different parser values."""
        plugin = ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="test-plugin",
            namespace="test_plugin",
            pip_url="test-plugin",
            capabilities=["structured-logging"],
        )

        invoker = self.create_invoker(project, plugin, parser_value)
        log_parser = invoker.get_log_parser()
        assert log_parser == expected

    def test_opt_out_of_singer_sdk_parser(self, project):
        """Test plugins can opt out of singer-sdk parser."""
        # Plugin that explicitly opts out to use default parser
        plugin_opt_out = ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="test-plugin-opt-out",
            namespace="test_plugin_opt_out",
            pip_url="test-plugin-opt-out",
            capabilities=["structured-logging"],
        )

        invoker = self.create_invoker(project, plugin_opt_out, "default")
        log_parser = invoker.get_log_parser()
        assert log_parser == "default"

    def test_default_behavior_no_parser(self, project):
        """Test plugins return None when no parser configured."""
        # Plugin with structured-logging capability but no explicit log parser config
        plugin_default = ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="test-plugin-default",
            namespace="test_plugin_default",
            pip_url="test-plugin-default",
            capabilities=["structured-logging", "catalog", "discover"],
        )

        invoker = self.create_invoker(project, plugin_default)
        log_parser = invoker.get_log_parser()
        assert log_parser is None
