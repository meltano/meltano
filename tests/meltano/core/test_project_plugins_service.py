from __future__ import annotations

import json
import shutil
import typing as t
from copy import deepcopy

import pytest

from meltano.core.plugin import BasePlugin, PluginType
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.project_plugins_service import (
    DefinitionSource,
    PluginDefinitionNotFoundError,
)

if t.TYPE_CHECKING:
    from meltano.core.locked_definition_service import LockedDefinitionService
    from meltano.core.project import Project


@pytest.fixture
def modified_lockfile(project: Project):
    lockfile_path = project.dirs.plugin_lock_path(
        PluginType.EXTRACTORS,
        "tap-mock",
        variant_name="meltano",
    )
    with lockfile_path.open() as lockfile:
        original_contents = json.load(lockfile)

    new_contents = deepcopy(original_contents)
    new_contents["settings"].append({"name": "foo"})

    with lockfile_path.open("w") as lockfile:
        json.dump(new_contents, lockfile)

    yield

    with lockfile_path.open("w") as lockfile:
        json.dump(original_contents, lockfile)


class TestProjectPluginsService:
    @pytest.fixture(autouse=True)
    def setup(self, project: Project, tap) -> None:
        project.plugins.lock_service.save(tap, exists_ok=True)

    @pytest.mark.order(0)
    def test_plugins(self, project) -> None:
        assert all(
            isinstance(plugin.parent, BasePlugin)
            for plugin in project.plugins.plugins()
        )

    def test_get_plugin(
        self,
        project,
        tap,
        alternative_tap,
        inherited_tap,
        alternative_target,
    ) -> None:
        # name="tap-mock", variant="meltano"
        plugin = project.plugins.get_plugin(tap)
        assert plugin.type == PluginType.EXTRACTORS
        assert plugin.name == "tap-mock"
        assert plugin.variant == "meltano"
        assert plugin.parent

        # name="tap-mock--singer-io", inherit_from="tap-mock", variant="singer-io"
        alternative_plugin = project.plugins.get_plugin(alternative_tap)
        assert alternative_plugin.type == PluginType.EXTRACTORS
        assert alternative_plugin.name == "tap-mock--singer-io"
        assert alternative_plugin.inherit_from == "tap-mock"
        assert alternative_plugin.variant == "singer-io"
        assert plugin.parent

        # name="tap-mock-inherited", inherit_from="tap-mock"
        inherited_plugin = project.plugins.get_plugin(inherited_tap)
        assert inherited_plugin.type == PluginType.EXTRACTORS
        assert inherited_plugin.name == "tap-mock-inherited"
        assert inherited_plugin.inherit_from == "tap-mock"
        assert plugin.parent

        # name="target-mock-alternative", inherit_from="target-mock"
        alternative_plugin = project.plugins.get_plugin(alternative_target)
        assert alternative_plugin.type == PluginType.LOADERS
        assert alternative_plugin.name == "target-mock-alternative"
        assert alternative_plugin.inherit_from == "target-mock"
        assert plugin.parent

        # Results are cached
        assert project.plugins.get_plugin(tap) is plugin

        project.refresh()
        assert project.plugins.get_plugin(tap) is not plugin

    @pytest.mark.order(2)
    @pytest.mark.usefixtures("modified_lockfile")
    def test_get_parent_from_lockfile(
        self,
        project: Project,
        tap: ProjectPlugin,
        locked_definition_service: LockedDefinitionService,
    ) -> None:
        expected = locked_definition_service.find_base_plugin(
            plugin_type=PluginType.EXTRACTORS,
            plugin_name="tap-mock",
            variant="meltano",
        )

        result, source = project.plugins.find_parent(tap)
        assert source == DefinitionSource.LOCKFILE
        assert result == expected
        assert result.settings == expected.settings
        assert result.settings[-1].name == "foo"

    @pytest.mark.order(2)
    def test_get_parent_no_source_enabled(
        self,
        project: Project,
        tap: ProjectPlugin,
    ) -> None:
        with (
            project.plugins.use_preferred_source(DefinitionSource.NONE),
            pytest.raises(PluginDefinitionNotFoundError),
        ):
            project.plugins.get_parent(tap)

    def test_get_parent_no_lockfiles(
        self,
        project: Project,
        tap,
        alternative_tap,
        inherited_tap,
        alternative_target,
    ) -> None:
        # The behavior being tested here assumes that no lockfiles exist.
        shutil.rmtree(
            project.plugins.project.dirs.root_dir("plugins"),
            ignore_errors=True,
        )
        # name="tap-mock", variant="meltano"
        # Shadows base plugin with correct variant
        parent = project.plugins.get_parent(tap)
        base = project.hub_service.find_base_plugin(
            plugin_type=PluginType.EXTRACTORS,
            plugin_name="tap-mock",
            variant="meltano",
        )
        assert base.name == parent.name
        assert base.type == parent.type

        # name="tap-mock-inherited", inherit_from="tap-mock"
        # Inherits from project plugin
        assert project.plugins.get_parent(inherited_tap) == tap

        # name="tap-mock--singer-io", inherit_from="tap-mock", variant="singer-io"
        # Inherits from base plugin with correct variant
        parent = project.plugins.get_parent(alternative_tap)
        base = project.hub_service.find_base_plugin(
            plugin_type=PluginType.EXTRACTORS,
            plugin_name="tap-mock",
            variant="singer-io",
        )
        assert base.name == parent.name
        assert base.type == parent.type

        # name="target-mock-alternative", inherit_from="target-mock"
        # Inherits from base plugin because no plugin shadowing the base plugin exists
        base = project.hub_service.find_base_plugin(
            plugin_type=PluginType.LOADERS,
            plugin_name="target-mock",
        )
        parent = project.plugins.get_parent(alternative_target)
        assert base.name == parent.name
        assert base.type == parent.type

        nonexistent_parent = ProjectPlugin(
            PluginType.EXTRACTORS,
            name="tap-foo",
            inherit_from="tap-bar",
        )
        with pytest.raises(PluginDefinitionNotFoundError) as excinfo:
            assert project.plugins.get_parent(nonexistent_parent)

        assert isinstance(excinfo.value.__cause__, PluginNotFoundError)

    def test_update_plugin(self, project: Project, tap) -> None:
        # update a tap with a random value
        tap.config["test"] = 42
        tap, outdated = project.plugins.update_plugin(tap)
        assert (
            project.plugins.get_plugin(tap).config["test"] == 42  # (OK magic number)
        )

        # revert back
        project.plugins.update_plugin(outdated)
        assert (
            project.plugins.get_plugin(tap).config == {}  # (OK compare with falsy)
        )

    def test_update_plugin_not_found(self, project: Project) -> None:
        nonexistent_plugin = ProjectPlugin(
            PluginType.EXTRACTORS,
            name="tap-foo",
        )

        with pytest.raises(PluginNotFoundError):
            project.plugins.update_plugin(nonexistent_plugin)

    def test_find_plugins_by_mapping_name(self, project: Project, mapper) -> None:
        assert project.plugins.find_plugins_by_mapping_name("mock-mapping-1") == [
            mapper,
        ]
        assert project.plugins.find_plugins_by_mapping_name("mock-mapping-0") == [
            mapper,
        ]
        with pytest.raises(PluginNotFoundError):
            project.plugins.find_plugins_by_mapping_name("non-existent-mapping")

    def test_find_plugins(self, project: Project, mapper) -> None:
        assert project.plugins.find_plugin("mock-mapping-1") == mapper
        assert project.plugins.find_plugin("mock-mapping-0") == mapper
        with pytest.raises(PluginNotFoundError):
            project.plugins.find_plugin("non-existent-mapping")
