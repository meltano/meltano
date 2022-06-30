from meltano.core.block.plugin_command import plugin_command_invoker
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.tracking import PluginsTrackingContext
from meltano.core.tracking.schemas import PluginsContextSchema
from meltano.core.utils import hash_sha256


class TestPluginsTrackingContext:
    def test_plugins_tracking_context_from_block(
        self,
        project,
        dbt: ProjectPlugin,
    ):
        cmd = plugin_command_invoker(
            dbt,
            project,
            command="test",
        )
        plugin_ctx = PluginsTrackingContext.from_block(cmd)
        assert plugin_ctx.schema == PluginsContextSchema.url
        assert len(plugin_ctx.data.get("plugins")) == 1
        plugin = plugin_ctx.data.get("plugins")[0]
        assert plugin.get("name_hash") == hash_sha256(dbt.name)
        assert plugin.get("namespace_hash") == hash_sha256(dbt.namespace)
        assert plugin.get("executable_hash") == hash_sha256(dbt.executable)
        assert plugin.get("variant_name_hash") == hash_sha256(dbt.variant)
        assert plugin.get("pip_url_hash") == hash_sha256(dbt.formatted_pip_url)
        assert plugin.get("parent_name_hash") == hash_sha256(dbt.parent.name)
        assert plugin.get("command") == "test"

    def test_plugins_tracking_context(self, tap: ProjectPlugin, dbt: ProjectPlugin):

        plugin_ctx = PluginsTrackingContext([(tap, None), (dbt, "test")])
        assert plugin_ctx.schema == PluginsContextSchema.url
        assert len(plugin_ctx.data.get("plugins")) == 2
        for plugin in plugin_ctx.data.get("plugins"):
            if plugin.get("category") == "extractors":
                assert plugin.get("name_hash") == hash_sha256(tap.name)
                assert plugin.get("namespace_hash") == hash_sha256(tap.namespace)
                assert plugin.get("executable_hash") == hash_sha256(tap.executable)
                assert plugin.get("variant_name_hash") == hash_sha256(tap.variant)
                assert plugin.get("pip_url_hash") == hash_sha256(tap.formatted_pip_url)
                assert plugin.get("parent_name_hash") == hash_sha256(tap.parent.name)
                assert plugin.get("command") is None
            elif plugin.get("category") == "transformers":
                assert plugin.get("name_hash") == hash_sha256(dbt.name)
                assert plugin.get("namespace_hash") == hash_sha256(dbt.namespace)
                assert plugin.get("executable_hash") == hash_sha256(dbt.executable)
                assert plugin.get("variant_name_hash") == hash_sha256(dbt.variant)
                assert plugin.get("pip_url_hash") == hash_sha256(dbt.formatted_pip_url)
                assert plugin.get("parent_name_hash") == hash_sha256(dbt.parent.name)
                assert plugin.get("command") == "test"

        # verify that passing a None object results in an empty plugin context.
        plugin_ctx = PluginsTrackingContext([(None, None)])
        assert plugin_ctx.data.get("plugins") == [{}]
