from __future__ import annotations

import json
import typing as t

import pytest

from meltano.core.plugin.base import BasePlugin, PluginDefinition, PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_lock_service import (
    LockfileAlreadyExistsError,
    PluginLockService,
)

if t.TYPE_CHECKING:
    from meltano.core.project import Project


@pytest.fixture
def plugin():
    plugin_definition = PluginDefinition(
        PluginType.EXTRACTORS,
        name="tap-locked",
        namespace="tap_locked",
        foo="bar",
        variants=[
            {
                "name": "meltano",
                "pip_url": "meltano-tap-locked",
                "repo": "https://gitlab.com/meltano/tap-locked",
                "baz": "qux",
            },
            {
                "name": "singer-io",
                "original": True,
                "deprecated": True,
                "pip_url": "tap-locked",
                "repo": "https://github.com/singer-io/tap-locked",
            },
        ],
    )
    variant = plugin_definition.find_variant("meltano")
    base_plugin = BasePlugin(plugin_definition, variant)

    parent_plugin = ProjectPlugin(
        base_plugin.type,
        base_plugin.name,
        variant="meltano",
    )
    parent_plugin.parent = base_plugin

    plugin = ProjectPlugin(
        base_plugin.type,
        f"{base_plugin.name}--two",
        inherit_from=parent_plugin.name,
    )
    plugin.parent = parent_plugin
    return plugin


class TestPluginLockService:
    @pytest.fixture
    def subject(self, project: Project):
        return PluginLockService(project)

    def test_save(self, subject: PluginLockService, plugin: ProjectPlugin) -> None:
        plugin_lock_path = subject.plugin_lock_path(
            plugin=plugin,
            variant_name=plugin.variant,
        )
        # Clean up any existing lockfile from previous tests
        plugin_lock_path.unlink(missing_ok=True)

        subject.save(plugin)
        assert plugin_lock_path.exists()

        with plugin_lock_path.open() as lock_file:
            lock_json = json.load(lock_file)
            assert lock_json["foo"] == "bar"
            assert lock_json["baz"] == "qux"

        with pytest.raises(LockfileAlreadyExistsError):
            subject.save(plugin)

    def test_get_standalone_data_without_lockfile(
        self,
        subject: PluginLockService,
        plugin: ProjectPlugin,
    ) -> None:
        """Test get_standalone_data when lock file doesn't exist.

        This tests the fallback path (line 228) where StandalonePlugin.from_variant
        is called to generate the standalone data when no lock file exists.
        """
        # Ensure no lock file exists (remove it if a previous test created it)
        plugin_lock_path = subject.plugin_lock_path(
            plugin=plugin,
            variant_name=plugin.variant,
        )
        plugin_lock_path.unlink(missing_ok=True)

        # Call get_standalone_data - should use the fallback path (line 228)
        standalone_data = subject.get_standalone_data(plugin)

        # Verify the data is correctly generated from the variant
        assert isinstance(standalone_data, dict)
        assert standalone_data["name"] == "tap-locked"
        assert standalone_data["namespace"] == "tap_locked"
        assert standalone_data["pip_url"] == "meltano-tap-locked"
        assert standalone_data["repo"] == "https://gitlab.com/meltano/tap-locked"
        # Should include both definition-level and variant-level attributes
        assert standalone_data["foo"] == "bar"
        assert standalone_data["baz"] == "qux"

        # Verify that no lock file was created by this call
        assert not plugin_lock_path.exists()

    def test_get_standalone_data_with_lockfile(
        self,
        subject: PluginLockService,
        plugin: ProjectPlugin,
    ) -> None:
        """Test get_standalone_data when lock file exists.

        This tests that when a lock file exists, it's loaded from disk
        rather than generated from the variant.
        """
        plugin_lock_path = subject.plugin_lock_path(
            plugin=plugin,
            variant_name=plugin.variant,
        )

        # Save the lock file (use exists_ok=True in case a previous test created it)
        subject.save(plugin, exists_ok=True)
        assert plugin_lock_path.exists()

        # Call get_standalone_data - should load from the existing lock file
        standalone_data = subject.get_standalone_data(plugin)

        # Verify the data matches what's in the lock file
        assert isinstance(standalone_data, dict)
        assert standalone_data["name"] == "tap-locked"
        assert standalone_data["namespace"] == "tap_locked"
        assert standalone_data["pip_url"] == "meltano-tap-locked"
        assert standalone_data["foo"] == "bar"
        assert standalone_data["baz"] == "qux"
