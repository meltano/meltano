from __future__ import annotations

import json
import typing as t

import pytest

from meltano.core.cloud.config import CLOUD_API_ROOT
from meltano.core.cloud.credentials import Credentials
from meltano.core.hub.client import HubConnectionError, MeltanoHubService
from meltano.core.plugin.base import BasePlugin, PluginDefinition, PluginType
from meltano.core.plugin.error import PluginNotFoundError
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


USER = {"name": "user", "label": "User"}
TOKEN = {"name": "token", "kind": "string", "sensitive": True}


def _definition(**variant: t.Any) -> PluginDefinition:
    return PluginDefinition(
        PluginType.EXTRACTORS,
        name="tap-served",
        namespace="tap_served",
        variants=[
            {
                "name": "meltano",
                "pip_url": "tap-served==1.0",
                "capabilities": ["catalog", "discover", "state"],
                "settings": [USER, TOKEN],
                **variant,
            },
        ],
    )


class TestHasUpdate:
    @pytest.fixture
    def subject(self, project: Project) -> PluginLockService:
        return PluginLockService(project)

    @pytest.fixture
    def locked(self, subject: PluginLockService) -> ProjectPlugin:
        """A plugin whose lock file holds the definition `_definition` gives."""
        definition = _definition()
        plugin = ProjectPlugin(PluginType.EXTRACTORS, "tap-served", variant="meltano")
        plugin.parent = BasePlugin(definition, definition.find_variant("meltano"))
        subject.save(plugin, exists_ok=True)
        return plugin

    @pytest.fixture
    def logged_in(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            MeltanoHubService,
            "cloud_credentials",
            staticmethod(lambda: Credentials(access_token="s3cr3t")),
        )
        monkeypatch.setattr(MeltanoHubService, "hub_api_url", CLOUD_API_ROOT)

    @staticmethod
    def serve(
        project: Project,
        monkeypatch: pytest.MonkeyPatch,
        served: PluginDefinition | Exception,
    ) -> None:
        def find_definition(*_args: t.Any, **kwargs: t.Any) -> PluginDefinition:
            # The check must not cost a request each time a plugin is run.
            assert kwargs["refresh"] is False
            if isinstance(served, Exception):
                raise served
            return served

        monkeypatch.setattr(project.hub_service, "find_definition", find_definition)

    @pytest.mark.usefixtures("logged_in")
    @pytest.mark.parametrize(
        ("variant", "changes"),
        (
            pytest.param({}, (), id="same"),
            pytest.param(
                {"pip_url": "tap-served==2.0"}, ("pip_url",), id="new-release"
            ),
            pytest.param(
                {"settings": [USER, TOKEN, {"name": "region"}]},
                ("settings",),
                id="setting-added",
            ),
            pytest.param(
                {"settings": [USER, {**TOKEN, "sensitive": False}]},
                ("settings",),
                id="setting-changed",
            ),
            pytest.param(
                {
                    "logo_url": "/assets/logos/extractors/served.png",
                    "docs": "https://example.com/tap-served",
                    "settings": [{**USER, "label": "User name"}, TOKEN],
                },
                (),
                id="presentation-changed",
            ),
            pytest.param(
                {
                    "capabilities": ["state", "discover", "catalog"],
                    "settings": [TOKEN, USER],
                },
                (),
                id="order-changed",
            ),
            pytest.param(
                {"capabilities": ["discover"], "settings": [USER]},
                ("capabilities", "settings"),
                id="several-changed",
            ),
        ),
    )
    def test_compares_how_the_plugin_runs(
        self,
        project: Project,
        subject: PluginLockService,
        locked: ProjectPlugin,
        monkeypatch: pytest.MonkeyPatch,
        variant: dict[str, t.Any],
        changes: tuple[str, ...],
    ) -> None:
        self.serve(project, monkeypatch, _definition(**variant))
        update = subject.check_update(locked)

        assert update is not None
        assert update.changes == changes
        assert update.available is bool(changes)

    def test_logged_out_user_is_not_checked(
        self,
        project: Project,
        subject: PluginLockService,
        locked: ProjectPlugin,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        self.serve(project, monkeypatch, AssertionError("The Hub was called"))
        assert subject.check_update(locked) is None

    @pytest.mark.usefixtures("logged_in")
    def test_own_hub_is_not_checked(
        self,
        project: Project,
        subject: PluginLockService,
        locked: ProjectPlugin,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(MeltanoHubService, "hub_api_url", "https://hub.example")
        self.serve(project, monkeypatch, AssertionError("The Hub was called"))
        assert subject.check_update(locked) is None

    @pytest.mark.usefixtures("logged_in")
    def test_custom_and_inherited_plugins_are_not_checked(
        self,
        project: Project,
        subject: PluginLockService,
        plugin: ProjectPlugin,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        self.serve(project, monkeypatch, AssertionError("The Hub was called"))
        custom = ProjectPlugin(
            PluginType.EXTRACTORS,
            "tap-custom",
            namespace="tap_custom",
            pip_url="tap-custom",
        )

        assert subject.check_update(custom) is None
        assert subject.check_update(plugin) is None

    @pytest.mark.usefixtures("logged_in")
    @pytest.mark.parametrize(
        "error",
        (
            PluginNotFoundError("tap-served"),
            HubConnectionError("Could not connect to Meltano Hub"),
        ),
    )
    def test_plugin_the_hub_cannot_serve_is_not_checked(
        self,
        project: Project,
        subject: PluginLockService,
        locked: ProjectPlugin,
        monkeypatch: pytest.MonkeyPatch,
        error: Exception,
    ) -> None:
        self.serve(project, monkeypatch, error)
        assert subject.check_update(locked) is None
