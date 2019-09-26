from typing import Optional
from collections import namedtuple

from meltano.core.project import Project
from meltano.core.config_service import ConfigService
from meltano.core.plugin import Plugin, PluginType, PluginRef
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.plugin_invoker import invoker_factory


class PluginContext(namedtuple("PluginContext", "ref install definition config")):
    @property
    def namespace(self):
        return self.definition.namespace

    @property
    def name(self):
        return self.install.name


class ELTContext:
    def __init__(
        self, project, loader: PluginContext, extractor: Optional[PluginContext] = None
    ):
        self.project = project
        self.loader = loader
        self.extractor = extractor

    def extractor_invoker(self):
        return invoker_factory(
            self.project, self.extractor.install, plugin_config=self.extractor.config
        )

    def loader_invoker(self):
        return invoker_factory(
            self.project, self.loader.install, plugin_config=self.loader.config
        )


class ELTContextBuilder:
    def __init__(
        self,
        project: Project,
        config_service: ConfigService = None,
        plugin_settings_service: PluginSettingsService = None,
        plugin_discovery_service: PluginDiscoveryService = None,
    ):
        self.project = project
        self.config_service = config_service or ConfigService(project)
        self.settings_service = plugin_settings_service or PluginSettingsService(
            project
        )
        self.discovery_service = plugin_discovery_service or PluginDiscoveryService(
            project
        )
        self._extractor = None
        self._loader = None

    def with_extractor(self, extractor_name: str):
        self._extractor = PluginRef(PluginType.EXTRACTORS, extractor_name)

        return self

    def with_loader(self, loader_name: str):
        self._loader = PluginRef(PluginType.LOADERS, loader_name)

        return self

    def plugin_context(self, session, plugin: PluginRef):
        return PluginContext(
            ref=plugin,
            install=self.config_service.find_plugin(
                plugin_name=plugin.name, plugin_type=plugin.type
            ),
            definition=self.discovery_service.find_plugin(
                plugin_name=plugin.name, plugin_type=plugin.type
            ),
            config=self.settings_service.as_config(session, plugin),
        )

    def context(self, session) -> ELTContext:
        return ELTContext(
            self.project,
            self.plugin_context(session, self._loader),
            extractor=self.plugin_context(session, self._extractor)
            if self._extractor
            else None,
        )
