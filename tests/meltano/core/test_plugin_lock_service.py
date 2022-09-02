from __future__ import annotations

import json

import pytest

from meltano.core.plugin.base import BasePlugin, PluginDefinition, PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_lock_service import (
    LockfileAlreadyExistsError,
    PluginLock,
    PluginLockService,
)
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
        variant=variant,
    )
    parent_plugin.parent = base_plugin

    plugin = ProjectPlugin(
        base_plugin.type,
        f"{base_plugin.name}--two",
        inherit_from=parent_plugin.name,
    )
    plugin.parent = parent_plugin
    return plugin


class TestPluginLock:
    @pytest.fixture
    def subject(self, project: Project, plugin: ProjectPlugin):
        return PluginLock(project, plugin)

    def test_path(self, subject: PluginLock):
        assert subject.path.parts[-3:] == (
            "plugins",
            "extractors",
            "tap-locked--meltano.lock",
        )

    @pytest.mark.order(before="test_load")
    def test_save(self, subject: PluginLock):
        assert not subject.path.exists()
        subject.save()
        assert subject.path.exists()

    def test_load(self, subject: PluginLock, plugin: ProjectPlugin):
        subject.save()
        loaded = subject.load()
        assert loaded.name == plugin.inherit_from
        assert loaded.variant == plugin.variant.name
        assert loaded.settings == plugin.settings


class TestPluginLockService:
    @pytest.fixture
    def subject(self, project: Project):
        return PluginLockService(project)

    def test_save(
        self,
        subject: PluginLockService,
        project: Project,
        plugin: ProjectPlugin,
    ):
        plugin_lock = PluginLock(project, plugin)
        assert not plugin_lock.path.exists()

        subject.save(plugin)
        assert plugin_lock.path.exists()

        with plugin_lock.path.open() as lock_file:
            lock_json = json.load(lock_file)
            assert lock_json["foo"] == "bar"
            assert lock_json["baz"] == "qux"

        with pytest.raises(LockfileAlreadyExistsError) as exc_info:
            subject.save(plugin)

        assert exc_info.value.plugin == plugin
