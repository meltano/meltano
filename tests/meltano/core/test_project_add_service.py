import pytest

from meltano.core.plugin import PluginType, Variant
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin.singer import SingerTap
from meltano.core.plugin_discovery_service import PluginNotFoundError
from meltano.core.project import Project
from meltano.core.project_add_service import ProjectAddService


class TestProjectAddService:
    @pytest.fixture
    def subject(self, project_add_service):
        return project_add_service

    def test_missing_plugin_exception(self, subject):
        with pytest.raises(PluginNotFoundError):
            subject.add(PluginType.EXTRACTORS, "tap-missing")

    @pytest.mark.parametrize(  # noqa: WPS317
        ("plugin_type", "plugin_name", "default_variant"),
        [
            (PluginType.EXTRACTORS, "tap-mock", "meltano"),
            (PluginType.LOADERS, "target-mock", None),
            (PluginType.TRANSFORMERS, "transformer-mock", None),
            (PluginType.TRANSFORMS, "tap-mock-transform", None),
            (PluginType.UTILITIES, "utility-mock", None),
        ],
    )
    def test_add(
        self,
        plugin_type,
        plugin_name,
        default_variant,
        subject: ProjectAddService,
        project: Project,
        plugin_discovery_service,
    ):
        added = subject.add(plugin_type, plugin_name)
        assert added in project.meltano["plugins"][plugin_type]
        assert project.plugin_lock_path(
            plugin_type,
            plugin_name,
            variant_name=default_variant,
        ).exists()

        # Variant and pip_url are repeated in
        # canonical representation for `meltano.yml`
        canonical = added.canonical()

        if default_variant:
            assert added.variant == default_variant
            assert canonical["variant"] == default_variant
        else:
            assert added.variant == Variant.DEFAULT_NAME
            assert "variant" not in canonical

        assert canonical["pip_url"] == added.pip_url

    def test_add_inherited(self, tap, subject, project_plugins_service):
        # Make sure tap-mock is not in the project as a project plugin
        project_plugins_service.remove_from_file(tap)

        # Inheriting from base plugin
        inherited = subject.add(
            PluginType.EXTRACTORS, "tap-mock-inherited", inherit_from="tap-mock"
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

    def test_lockfile_inherited(self, subject: ProjectAddService):
        child = subject.add(
            PluginType.EXTRACTORS,
            "tap-mock-inherited-new",
            inherit_from="tap-mock",
        )
        assert isinstance(child.parent, SingerTap)
        assert child.parent.name == "tap-mock"

        parent_path = subject.project.plugin_lock_path(
            PluginType.EXTRACTORS,
            "tap-mock",
            variant_name="meltano",
        )
        assert parent_path.stem == "tap-mock--meltano"
        assert parent_path.exists()

        child_path = subject.project.plugin_lock_path(
            child.type,
            child.name,
            child.variant,
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
        assert grandchild.parent.parent.name == "tap-mock"

        grandchild_path = subject.project.plugin_lock_path(
            grandchild.type,
            grandchild.name,
            grandchild.variant,
        )
        assert grandchild_path.stem == "tap-mock-inherited-new-2--meltano"
        assert not grandchild_path.exists()

        matches = list(parent_path.parent.glob("tap-mock-inherited-new*"))
        assert not matches
