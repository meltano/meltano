from __future__ import annotations

import json

from meltano.core.plugin import PluginType
from meltano.core.plugin.base import PluginRef
from meltano.core.plugin.error import PluginExecutionError
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin.singer.catalog import ListSelectedExecutor
from meltano.core.plugin_invoker import invoker_factory
from meltano.core.project_plugins_service import ProjectPluginsService

from .project import Project


class SelectService:
    def __init__(
        self,
        project: Project,
        extractor: str,
        plugins_service: ProjectPluginsService = None,
    ):
        self.project = project
        self.plugins_service = plugins_service or ProjectPluginsService(project)
        self._extractor = self.plugins_service.find_plugin(
            extractor, PluginType.EXTRACTORS
        )

    @property
    def extractor(self) -> ProjectPlugin:
        """Retrieve extractor ProjectPlugin object."""
        return self._extractor

    @property
    def current_select(self):
        plugin_settings_service = PluginSettingsService(
            self.project,
            self.extractor,
            plugins_service=self.plugins_service,
        )
        return plugin_settings_service.get("_select")

    async def load_catalog(self, session):
        """Load the catalog."""
        invoker = invoker_factory(
            self.project,
            self.extractor,
            plugins_service=self.plugins_service,
        )

        async with invoker.prepared(session):
            catalog_json = await invoker.dump("catalog")

        return json.loads(catalog_json)

    async def list_all(self, session) -> ListSelectedExecutor:
        """List all select."""
        try:
            catalog = await self.load_catalog(session)
        except FileNotFoundError as err:
            raise PluginExecutionError(
                "Could not find catalog. Verify that the tap supports discovery "
                + "mode and advertises the `discover` capability as well as either "
                + "`catalog` or `properties`"
            ) from err

        list_all = ListSelectedExecutor()
        list_all.visit(catalog)

        return list_all

    def update(self, entities_filter, attributes_filter, exclude, remove=False):
        """Update plugins' select patterns."""
        plugin: PluginRef

        if self.project.active_environment is None:
            plugin = self.extractor
        else:
            plugin = self.project.active_environment.get_plugin_config(
                self.extractor.type, self.extractor.name
            )

        this_pattern = self._get_pattern_string(
            entities_filter, attributes_filter, exclude
        )
        patterns = plugin.extras.get("select", [])
        if remove:
            patterns.remove(this_pattern)
        else:
            patterns.append(this_pattern)
        plugin.extras["select"] = patterns

        if self.project.active_environment is None:
            self.plugins_service.update_plugin(plugin)
        else:
            self.plugins_service.update_environment_plugin(plugin)

    @staticmethod
    def _get_pattern_string(entities_filter, attributes_filter, exclude) -> str:
        """Return a select pattern in string form."""
        exclude = "!" if exclude else ""
        return f"{exclude}{entities_filter}.{attributes_filter}"
