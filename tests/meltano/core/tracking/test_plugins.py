from __future__ import annotations

from typing import Any

from meltano.core.block.plugin_command import plugin_command_invoker
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.project import Project
from meltano.core.tracking.contexts import PluginsTrackingContext
from meltano.core.tracking.schemas import PluginsContextSchema
from meltano.core.utils import hash_sha256


class TestPluginsTrackingContext:
    def test_plugins_tracking_context_from_block(
        self,
        project: Project,
        dbt: ProjectPlugin,
    ):
        plugin_ctx = PluginsTrackingContext.from_block(
            plugin_command_invoker(
                dbt,
                project,
                command="test",
            )
        )
        assert plugin_ctx.schema == PluginsContextSchema.url
        assert len(plugin_ctx.data.get("plugins")) == 1
        plugin_dict = plugin_ctx.data.get("plugins")[0]
        self.assert_plugin_attributes(plugin_dict, dbt)
        assert plugin_dict.get("command") == "test"

    def test_plugins_tracking_context(self, tap: ProjectPlugin, dbt: ProjectPlugin):
        plugin_ctx = PluginsTrackingContext([(tap, None), (dbt, "test")])
        assert plugin_ctx.schema == PluginsContextSchema.url
        assert len(plugin_ctx.data.get("plugins")) == 2
        for plugin_dict in plugin_ctx.data.get("plugins"):
            if plugin_dict.get("category") == "extractors":
                self.assert_plugin_attributes(plugin_dict, tap)
                assert plugin_dict.get("command") is None
            elif plugin_dict.get("category") == "transformers":
                self.assert_plugin_attributes(plugin_dict, dbt)
                assert plugin_dict.get("command") == "test"

        # verify that passing a None object results in an empty plugin context.
        plugin_ctx = PluginsTrackingContext([(None, None)])
        assert plugin_ctx.data.get("plugins") == [{}]

        # verify that passing a plugin with no parent does not result in an error.
        # most likely this is a plugin that is not installed and is being removed or somehow referenced.
        tap.parent = None
        plugin_ctx = PluginsTrackingContext([(tap, None)])
        assert len(plugin_ctx.data.get("plugins")) == 1
        plugin_with_no_parent = plugin_ctx.data.get("plugins")[0]
        assert plugin_with_no_parent.get("name_hash") == hash_sha256(tap.name)
        assert not plugin_with_no_parent.get("parent_name_hash")

    @staticmethod
    def assert_plugin_attributes(plugin_dict: dict[str, Any], plugin: ProjectPlugin):
        for dict_key, plugin_key in (
            ("name_hash", "name"),
            ("namespace_hash", "namespace"),
            ("executable_hash", "executable"),
            ("variant_name_hash", "variant"),
            ("pip_url_hash", "pip_url"),
        ):
            assert plugin_dict.get(dict_key) == hash_sha256(getattr(plugin, plugin_key))
        assert plugin_dict.get("parent_name_hash") == hash_sha256(plugin.parent.name)
