"""Test plugin-level requires_meltano compatibility checking."""

from __future__ import annotations

import importlib.resources
import json
from unittest import mock

import pytest
from jsonschema import ValidationError, validate

from meltano import schemas
from meltano.core.plugin.base import (
    PluginDefinition,
    PluginType,
    StandalonePlugin,
    Variant,
)
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.plugin_lock_service import PluginLockService
from meltano.core.utils import IncompatibleMeltanoVersionError, get_meltano_version


class TestPluginCompatibility:
    """Test plugin-level Meltano version compatibility."""

    def test_plugin_without_requires_meltano(self):
        """Test that plugins without requires_meltano don't raise errors."""
        plugin = ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="tap-test",
            namespace="tap_test",
        )
        plugin.ensure_compatible()

    def test_plugin_with_compatible_requires_meltano(self):
        """Test that plugins with compatible requires_meltano don't raise errors."""
        current = get_meltano_version()
        plugin = ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="tap-test",
            namespace="tap_test",
            requires_meltano=f"=={current}",
        )
        plugin.ensure_compatible()

    def test_plugin_with_incompatible_requires_meltano(self):
        """Test that plugins with incompatible requires_meltano raise errors."""
        plugin = ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="tap-test",
            namespace="tap_test",
            requires_meltano="==999.0.0",
        )
        with pytest.raises(IncompatibleMeltanoVersionError):
            plugin.ensure_compatible()

    def test_plugin_invoker_compatibility_check(self, project):
        """Test that PluginInvoker checks compatibility during initialization."""
        plugin = ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="tap-test",
            namespace="tap_test",
            requires_meltano="==999.0.0",
        )
        with pytest.raises(IncompatibleMeltanoVersionError):
            PluginInvoker(project, plugin)

    def test_plugin_invoker_with_compatible_plugin(self, project):
        """Test that PluginInvoker works with compatible plugins."""
        current = get_meltano_version()
        plugin = ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="tap-test",
            namespace="tap_test",
            requires_meltano=f"=={current}",
        )
        # Should not raise an exception
        PluginInvoker(project, plugin)

    def test_plugin_inheritance_of_requires_meltano(self):
        """Test that plugins can inherit requires_meltano from parent."""
        # Create a parent plugin with requires_meltano
        parent = ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="parent-tap",
            namespace="parent_tap",
            requires_meltano="==999.0.0",
        )

        # Create a child plugin that inherits from parent
        child = ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="child-tap",
            inherit_from="parent-tap",
        )
        child.parent = parent

        # Child should inherit the incompatible requirement
        with pytest.raises(IncompatibleMeltanoVersionError):
            child.ensure_compatible()

    def test_plugin_requires_meltano_complex_specifier(self):
        """Test complex version specifiers work correctly."""
        plugin = ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="tap-test",
            namespace="tap_test",
            requires_meltano=">=1.0.0,<2.0.0",
        )

        # This should work if current version is in range
        with mock.patch("meltano.core.utils.get_meltano_version", return_value="1.0.0"):
            plugin.ensure_compatible()

        with (
            mock.patch("meltano.core.utils.get_meltano_version", return_value="2.0.0"),
            pytest.raises(IncompatibleMeltanoVersionError),
        ):
            plugin.ensure_compatible()

    def test_variant_requires_meltano(self):
        """Test that Variant class supports requires_meltano field."""
        variant = Variant(
            name="test",
            requires_meltano=">=3.0.0",
            pip_url="git+https://github.com/test/test.git",
        )
        assert variant.requires_meltano == ">=3.0.0"

    def test_standalone_plugin_requires_meltano(self):
        """Test that StandalonePlugin class supports requires_meltano field."""
        plugin = StandalonePlugin(
            plugin_type="extractors",
            name="tap-test",
            namespace="tap_test",
            requires_meltano=">=2.5.0",
        )
        assert plugin.requires_meltano == ">=2.5.0"

    def test_standalone_plugin_from_variant(self):
        """Test that StandalonePlugin.from_variant preserves requires_meltano."""
        variant = Variant(
            name="test-variant",
            requires_meltano=">=1.5.0",
        )
        plugin_def = PluginDefinition(
            PluginType.EXTRACTORS,
            "tap-test",
            "tap_test",
        )
        standalone = StandalonePlugin.from_variant(variant, plugin_def)
        assert standalone.requires_meltano == ">=1.5.0"

    def test_plugin_definition_from_standalone(self):
        """Test that PluginDefinition.from_standalone preserves requires_meltano."""
        standalone = StandalonePlugin(
            plugin_type="extractors",
            name="tap-test",
            namespace="tap_test",
            requires_meltano=">=3.5.0",
        )
        plugin_def = PluginDefinition.from_standalone(standalone)
        # The requires_meltano should be in the first variant
        assert plugin_def.variants[0].requires_meltano == ">=3.5.0"

    def test_standalone_from_variant_preserves_supported_python_versions(self):
        """Test that StandalonePlugin.from_variant preserves supported_python_versions."""  # noqa: E501
        variant = Variant(
            name="test-variant",
            supported_python_versions=["3.11", "3.12"],
        )
        plugin_def = PluginDefinition(
            PluginType.EXTRACTORS,
            "tap-test",
            "tap_test",
        )
        standalone = StandalonePlugin.from_variant(variant, plugin_def)
        assert standalone.supported_python_versions == ["3.11", "3.12"]

    def test_definition_from_standalone_preserves_supported_python_versions(self):
        """Test that PluginDefinition.from_standalone preserves supported_python_versions."""  # noqa: E501
        standalone = StandalonePlugin(
            plugin_type="extractors",
            name="tap-test",
            namespace="tap_test",
            supported_python_versions=["3.10", "3.11", "3.12"],
        )
        plugin_def = PluginDefinition.from_standalone(standalone)
        # The supported_python_versions should be in the first variant
        assert plugin_def.variants[0].supported_python_versions == [
            "3.10",
            "3.11",
            "3.12",
        ]

    def test_lockfile_serialization_includes_requires_meltano(self, project):
        """Test that plugin lockfiles include requires_meltano field."""
        # Create a plugin with requires_meltano
        plugin = ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="tap-test",
            namespace="tap_test",
            requires_meltano=">=2.0.0",
        )
        lock_service = PluginLockService(project)

        # Create a mock plugin definition for the lockfile
        plugin_def = PluginDefinition(
            PluginType.EXTRACTORS,
            "tap-test",
            "tap_test",
            variant="default",
            requires_meltano=">=2.0.0",
        )
        plugin._plugin_def = plugin_def
        plugin._variant = plugin_def.variants[0]

        # Create and save lockfile
        path = lock_service.save(plugin)

        # Read and verify lockfile content
        with path.open() as f:
            lockfile_data = json.load(f)

        assert lockfile_data["requires_meltano"] == ">=2.0.0"

    def test_incompatible_plugin_error_message(self):
        """Test that incompatible plugin errors have correct message format."""
        plugin = ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="tap-test",
            namespace="tap_test",
            requires_meltano="==999.0.0",
        )

        with pytest.raises(IncompatibleMeltanoVersionError) as exc_info:
            plugin.ensure_compatible()

        error = exc_info.value
        current_version = get_meltano_version()
        expected_message = (
            f"Project requires Meltano ==999.0.0, but {current_version} is installed"
        )
        assert str(error) == expected_message
        assert isinstance(error, IncompatibleMeltanoVersionError)
        assert error.required_version == "==999.0.0"
        assert error.current_version == current_version

    def test_plugin_without_requires_meltano_has_none_value(self):
        """Test that plugins without requires_meltano have None value."""
        plugin = ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="tap-test",
            namespace="tap_test",
        )
        assert plugin.requires_meltano is None

    def test_plugin_requires_meltano_inheritance_override(self):
        """Test that child plugin can override parent's requires_meltano."""
        # Create a parent plugin with requires_meltano
        parent = ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="parent-tap",
            namespace="parent_tap",
            requires_meltano=">=1.0.0",
        )

        # Create a child plugin that overrides requires_meltano
        current = get_meltano_version()
        child = ProjectPlugin(
            plugin_type=PluginType.EXTRACTORS,
            name="child-tap",
            inherit_from="parent-tap",
            requires_meltano=f"=={current}",  # Override with compatible version
        )
        child.parent = parent

        # Child should use its own requirement, not inherit from parent
        assert child.requires_meltano == f"=={current}"
        # This should not raise an error since child has compatible version
        child.ensure_compatible()

    def test_requires_meltano_works_across_plugin_types(self):
        """Test that requires_meltano works for different plugin types."""
        current = get_meltano_version()

        # Test different plugin types
        plugin_types = [
            PluginType.EXTRACTORS,
            PluginType.LOADERS,
            PluginType.TRANSFORMERS,
            PluginType.ORCHESTRATORS,
            PluginType.UTILITIES,
        ]

        for plugin_type in plugin_types:
            plugin = ProjectPlugin(
                plugin_type=plugin_type,
                name=f"test-{plugin_type.value}",
                namespace=f"test_{plugin_type.value}",
                requires_meltano=f"=={current}",
            )
            # Should not raise an error for any plugin type
            plugin.ensure_compatible()

    def test_plugin_canonical_serialization_includes_requires_meltano(self):
        """Test that plugin canonical representation includes requires_meltano."""
        plugin = StandalonePlugin(
            plugin_type="extractors",
            name="tap-test",
            namespace="tap_test",
            requires_meltano=">=1.0.0",
        )

        canonical_data = plugin.canonical()
        assert isinstance(canonical_data, dict)
        assert canonical_data["requires_meltano"] == ">=1.0.0"

    def test_json_schema_validates_plugin_requires_meltano(self):
        """Test that the JSON schema validates plugin-level requires_meltano."""
        # Load the Meltano JSON schema
        schema_resource = importlib.resources.files(schemas) / "meltano.schema.json"
        with schema_resource.open("r") as f:
            schema = json.load(f)

        # Test valid configuration with plugin-level requires_meltano
        valid_config = {
            "version": 1,
            "plugins": {
                "extractors": [
                    {
                        "name": "tap-gitlab",
                        "variant": "meltanolabs",
                        "requires_meltano": ">=3.0.0",
                    }
                ],
                "loaders": [
                    {
                        "name": "target-jsonl",
                        "requires_meltano": ">=2.5.0,<4.0.0",
                    }
                ],
            },
        }

        # Should not raise ValidationError
        validate(instance=valid_config, schema=schema)

        # Test invalid configuration (non-string requires_meltano)
        invalid_config = {
            "version": 1,
            "plugins": {
                "extractors": [
                    {
                        "name": "tap-gitlab",
                        "requires_meltano": 123,  # Invalid: should be string
                    }
                ]
            },
        }

        # Should raise ValidationError
        with pytest.raises(ValidationError):
            validate(instance=invalid_config, schema=schema)
