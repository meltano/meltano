from __future__ import annotations

import typing as t
from unittest import mock

import pytest

from meltano.core.constants import STATE_ID_COMPONENT_DELIMITER
from meltano.core.plugin import PluginType, Variant
from meltano.core.plugin.base import (
    BasePlugin,
    PluginRefNameContainsStateIdDelimiterError,
)
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin.singer import SingerTap
from meltano.core.project_plugins_service import PluginDefinitionNotFoundError

if t.TYPE_CHECKING:
    from collections import Counter

    from meltano.core.project import Project
    from meltano.core.project_add_service import ProjectAddService


class TestProjectAddService:
    @pytest.fixture
    def subject(self, project_add_service):
        return project_add_service

    def test_missing_plugin_exception(self, subject, hub_request_counter) -> None:
        with pytest.raises(PluginDefinitionNotFoundError):
            subject.add(PluginType.EXTRACTORS, "tap-missing")

        assert hub_request_counter["/extractors/index"] == 1
        assert len(hub_request_counter) == 1

    @pytest.mark.order(0)
    @pytest.mark.parametrize(
        ("plugin_type", "plugin_name", "variant", "default_variant"),
        (
            (PluginType.EXTRACTORS, "tap-mock", "meltano", "meltano"),
            (PluginType.LOADERS, "target-mock", None, "original"),
            (PluginType.TRANSFORMERS, "transformer-mock", None, "original"),
            (PluginType.TRANSFORMS, "tap-mock-transform", None, "original"),
            (PluginType.UTILITIES, "utility-mock", None, "original"),
        ),
    )
    def test_add(
        self,
        plugin_type: PluginType,
        plugin_name: str,
        variant: str,
        default_variant: str,
        subject: ProjectAddService,
        project: Project,
        hub_request_counter: Counter,
    ) -> None:
        used_variant = variant or default_variant
        lockfile_path = project.dirs.plugin_lock_path(
            plugin_type,
            plugin_name,
            variant_name=used_variant,
        )
        assert not lockfile_path.exists()

        added = subject.add(plugin_type, plugin_name)
        assert added in project.meltano["plugins"][plugin_type]
        assert lockfile_path.exists()

        # Variant and pip_url are repeated in
        # canonical representation for `meltano.yml`
        canonical = added.canonical()
        assert isinstance(canonical, dict)

        if default_variant:
            assert added.variant == default_variant
            assert canonical["variant"] == default_variant
        else:
            assert added.variant == Variant.DEFAULT_NAME
            assert "variant" not in canonical

        assert canonical["pip_url"] == added.pip_url

        assert hub_request_counter[f"/{plugin_type}/index"] == 1
        assert hub_request_counter[f"/{plugin_type}/{plugin_name}--{used_variant}"] == 1
        assert len(hub_request_counter) == 2

    def test_add_inherited(
        self,
        tap,
        subject,
        project: Project,
        hub_request_counter,
    ) -> None:
        # Make sure tap-mock is not in the project as a project plugin
        project.plugins.remove_from_file(tap)

        # Inheriting from base plugin
        inherited = subject.add(
            PluginType.EXTRACTORS,
            "tap-mock-inherited",
            inherit_from="tap-mock",
        )
        assert inherited.canonical() == {
            "name": "tap-mock-inherited",
            "inherit_from": "tap-mock",
            "variant": "meltano",
            "pip_url": "tap-mock",
        }

        # Inheriting from other project plugin
        inception = subject.add(
            PluginType.EXTRACTORS,
            "tap-mock-inception",
            inherit_from="tap-mock-inherited",
        )
        assert inception.canonical() == {
            "name": "tap-mock-inception",
            "inherit_from": "tap-mock-inherited",
        }

        assert hub_request_counter["/extractors/index"] == 1
        assert hub_request_counter["/extractors/tap-mock--meltano"] == 1
        assert len(hub_request_counter) == 2

    @pytest.mark.order(after="test_add_inherited")
    def test_lockfile_inherited(
        self,
        subject: ProjectAddService,
        hub_request_counter: Counter,
    ) -> None:
        child = subject.add(
            PluginType.EXTRACTORS,
            "tap-mock-inherited-new",
            inherit_from="tap-mock",
        )
        assert isinstance(child.parent, SingerTap)
        assert child.parent.name == "tap-mock"

        parent_path = subject.project.dirs.plugin_lock_path(
            plugin_type=PluginType.EXTRACTORS,
            plugin_name="tap-mock",
            variant_name="meltano",
        )
        assert parent_path.stem == "tap-mock--meltano"
        assert parent_path.exists()

        child_path = subject.project.dirs.plugin_lock_path(
            plugin_type=child.type,
            plugin_name=child.name,
            variant_name=child.variant,
        )
        assert child_path.stem == "tap-mock-inherited-new--meltano"
        assert not child_path.exists()

        grandchild = subject.add(
            PluginType.EXTRACTORS,
            "tap-mock-inherited-new-2",
            inherit_from="tap-mock-inherited-new",
        )
        assert isinstance(grandchild.parent, ProjectPlugin)
        assert grandchild.parent.name == "tap-mock-inherited-new"

        assert isinstance(grandchild.parent.parent, BasePlugin)
        assert grandchild.parent.parent.name == "tap-mock"

        grandchild_path = subject.project.dirs.plugin_lock_path(
            plugin_type=grandchild.type,
            plugin_name=grandchild.name,
            variant_name=grandchild.variant,
        )
        assert grandchild_path.stem == "tap-mock-inherited-new-2--meltano"
        assert not grandchild_path.exists()

        matches = list(parent_path.parent.glob("tap-mock-inherited-new*"))
        assert not matches

        assert hub_request_counter["/extractors/index"] == 1
        assert hub_request_counter["/extractors/tap-mock--meltano"] == 1
        assert len(hub_request_counter) == 2

    def test_add_name_contains_state_id_component_delimiter(
        self,
        subject: ProjectAddService,
    ) -> None:
        with pytest.raises(PluginRefNameContainsStateIdDelimiterError):
            subject.add(
                PluginType.EXTRACTORS,
                f"tap-mock{STATE_ID_COMPONENT_DELIMITER}",
            )

    @mock.patch("meltano.core.plugin_lock_service.PluginLockService.save")
    def test_add_update(
        self,
        lock_save: mock.MagicMock,
        target,
        subject: ProjectAddService,
        project: Project,
        hub_request_counter: Counter,
    ) -> None:
        target.config = {
            "username": "meltano",
            "password": "meltano",
        }

        project.plugins.update_plugin(target)

        updated_attrs = {
            "label": "Mock",
            "description": "Mock target",
            "executable": "./target-mock.sh",
            "settings": [
                {"name": "username"},
                {"name": "password"},
            ],
        }

        assert not target.canonical().items() >= updated_attrs.items()

        updated = subject.add(
            target.type,
            target.name,
            update=True,
            **updated_attrs,
        )

        assert hub_request_counter["/loaders/index"] == 1
        assert hub_request_counter["/loaders/target-mock--original"] == 1
        assert len(hub_request_counter) == 2

        assert lock_save.call_count == 1

        assert updated in project.meltano["plugins"][target.type]

        plugin_dict = updated.canonical()
        assert isinstance(plugin_dict, dict)
        assert plugin_dict.items() >= updated_attrs.items()
        assert updated.config_with_extras

    @mock.patch("meltano.core.plugin_lock_service.PluginLockService.save")
    def test_add_update_custom(
        self,
        lock_save: mock.MagicMock,
        subject: ProjectAddService,
        project: Project,
        hub_request_counter: Counter,
    ) -> None:
        custom_plugin = subject.add(
            PluginType.EXTRACTORS,
            "tap-custom",
            namespace="tap_custom",
            config={
                "username": "meltano",
                "password": "meltano",
                "start_date": "2023-01-01",
            },
        )

        updated_attrs = {
            "label": "Custom",
            "description": "Custom tap",
            "executable": "./tap-custom.sh",
            "settings": [
                {"name": "username"},
                {"name": "password"},
            ],
        }

        updated = subject.add(
            custom_plugin.type,
            custom_plugin.name,
            update=True,
            namespace=custom_plugin.namespace,
            **updated_attrs,
        )

        assert len(hub_request_counter) == 0

        assert lock_save.call_count == 0

        assert updated in project.meltano["plugins"][custom_plugin.type]

        plugin_dict = updated.canonical()
        assert isinstance(plugin_dict, dict)
        assert plugin_dict.items() >= updated_attrs.items()
        assert updated.config_with_extras
