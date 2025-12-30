from __future__ import annotations  # noqa: D100

import json
import typing as t

from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginExecutionError
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin.singer.catalog import ListSelectedExecutor
from meltano.core.plugin_invoker import invoker_factory

if t.TYPE_CHECKING:
    from sqlalchemy.orm.session import Session

    from meltano.core.environment import EnvironmentPluginConfig
    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project


class SelectService:  # noqa: D101
    def __init__(self, project: Project, extractor: str):
        """Initialize a `SelectService` instance.

        Args:
            project: The Meltano project being operated on.
            extractor: The name of the extractor plugin.
        """
        self.project = project
        self._extractor = self.project.plugins.find_plugin(
            extractor,
            plugin_type=PluginType.EXTRACTORS,
        )

    @property
    def extractor(self) -> ProjectPlugin:
        """Retrieve extractor ProjectPlugin object."""
        return self._extractor

    @property
    def current_select(self) -> list[str]:
        """Get the current select patterns.

        Returns:
            The current select pattern.
        """
        plugin_settings_service = PluginSettingsService(self.project, self.extractor)
        return plugin_settings_service.get("_select")

    async def load_catalog(self, session: Session, *, refresh: bool = False) -> dict:
        """Load the catalog."""
        invoker = invoker_factory(self.project, self.extractor)

        if refresh:
            invoker.settings_service.config_override["_use_cached_catalog"] = False

        async with invoker.prepared(session):
            catalog_json = await invoker.dump("catalog")

        return json.loads(catalog_json)

    async def list_all(
        self,
        session: Session,
        *,
        refresh: bool = False,
    ) -> ListSelectedExecutor:
        """List all select."""
        try:
            catalog = await self.load_catalog(session, refresh=refresh)
        except FileNotFoundError as err:
            raise PluginExecutionError(  # noqa: TRY003
                "Could not find catalog. Verify that the tap supports discovery "  # noqa: EM101
                "mode and advertises the `discover` capability as well as either "
                "`catalog` or `properties`",
            ) from err

        list_all = ListSelectedExecutor()

        # TODO: revisit the visit_with decorator when mypy has better support
        # for class decorators
        # https://github.com/python/mypy/issues/3135
        list_all.visit(catalog)  # type: ignore[attr-defined]

        return list_all

    def clear(self) -> None:
        """Clear all select patterns for the extractor."""
        plugin: ProjectPlugin | EnvironmentPluginConfig
        if self.project.environment is None:
            plugin = self.extractor
            if "select" in plugin.extras:
                del plugin.extras["select"]
            self.project.plugins.update_plugin(plugin)
        else:
            plugin = self.project.environment.get_plugin_config(
                self.extractor.type,
                self.extractor.name,
            )
            if "select" in plugin.extras:
                del plugin.extras["select"]
            self.project.plugins.update_environment_plugin(plugin)

    def update(
        self,
        streams_filter: str,
        properties_filter: str,
        exclude: bool,  # noqa: FBT001
        *,
        remove: bool = False,
    ) -> None:
        """Update plugins' select patterns."""
        this_pattern = self._get_pattern_string(
            streams_filter,
            properties_filter,
            exclude,
        )

        plugin: ProjectPlugin | EnvironmentPluginConfig
        if self.project.environment is None:
            plugin = self.extractor
            self._update_plugin_select(plugin, this_pattern, remove=remove)
            self.project.plugins.update_plugin(plugin)
        else:
            plugin = self.project.environment.get_plugin_config(
                self.extractor.type,
                self.extractor.name,
            )
            self._update_plugin_select(plugin, this_pattern, remove=remove)
            self.project.plugins.update_environment_plugin(plugin)

    def _update_plugin_select(
        self,
        plugin: ProjectPlugin | EnvironmentPluginConfig,
        pattern: str,
        *,
        remove: bool = False,
    ) -> None:
        """Update the plugin's select patterns."""
        patterns = plugin.extras.get("select", [])
        if remove:
            patterns.remove(pattern)
        else:
            patterns.append(pattern)

        plugin.extras["select"] = patterns

    @staticmethod
    def _get_pattern_string(
        streams_filter: str,
        properties_filter: str,
        exclude: bool,  # noqa: FBT001
    ) -> str:
        """Return a select pattern in string form."""
        exclude_char = "!" if exclude else ""
        return f"{exclude_char}{streams_filter}.{properties_filter}"
