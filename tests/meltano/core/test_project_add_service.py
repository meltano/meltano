import os
import shutil

import pytest
import yaml
from meltano.core.plugin import PluginType, Variant
from meltano.core.plugin_discovery_service import PluginNotFoundError
from meltano.core.project_add_service import ProjectAddService


class TestProjectAddService:
    @pytest.fixture
    def subject(self, project_add_service):
        return project_add_service

    def test_missing_plugin_exception(self, subject):
        try:
            subject.add(PluginType.EXTRACTORS, "tap-missing")
        except Exception as e:
            assert type(e) is PluginNotFoundError

    @pytest.mark.parametrize(
        ("plugin_type", "plugin_name", "default_variant"),
        [
            (PluginType.EXTRACTORS, "tap-mock", "meltano"),
            (PluginType.LOADERS, "target-mock", None),
            (PluginType.TRANSFORMERS, "transformer-mock", None),
            (PluginType.TRANSFORMS, "tap-mock-transform", None),
        ],
    )
    def test_add(
        self,
        plugin_type,
        plugin_name,
        default_variant,
        subject,
        project,
        plugin_discovery_service,
    ):
        added = subject.add(plugin_type, plugin_name)
        assert added in project.meltano["plugins"][plugin_type]

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
