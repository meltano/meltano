from typing import Optional

from meltano.core.project import Project
from meltano.core.config_service import ConfigService
from meltano.core.plugin import Plugin, PluginType, PluginRef
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.plugin_invoker import invoker_factory


class ELTContext():
    def __init__(self,
                 project,
                 loader: Plugin,
                 extractor: Optional[Plugin] = None,
                 namespace: Optional[str] = None):
        self.project = project
        self.loader = loader
        self.extractor = extractor
        self.namespace = namespace

        self.loader_config = None
        self.extractor_config = None

    def extractor_invoker(self):
        return invoker_factory(self.project, self.extractor, plugin_config = self.extractor_config)

    def loader_invoker(self):
        return invoker_factory(self.project, self.loader, plugin_config = self.loader_config)


class ELTContextBuilder():
    def __init__(self,
                 project: Project,
                 config_service: ConfigService = None,
                 plugin_settings_service: PluginSettingsService = None,
                 plugin_discovery_service: PluginDiscoveryService = None):
        self.project = project
        self.config_service = config_service or ConfigService(project)
        self.settings_service = plugin_settings_service or PluginSettingsService(project)
        self.discovery_service = plugin_discovery_service or PluginDiscoveryService(project)
        self._extractor = None
        self._loader = None
        self._model = None
        self._namespace = None

    @property
    def namespace(self):
        return self._namespace

    def plugin_namespace(self, plugin: PluginRef) -> str:
        plugin_def = self.discovery_service.find_plugin(plugin.type, plugin.name)

        return plugin_def.namespace

    def with_extractor(self, extractor_name: str):
        plugin = PluginRef(PluginType.EXTRACTORS, extractor_name)
        namespace = self.plugin_namespace(plugin)

        if self._namespace is not None and self._namespace != namespace:
            raise IncompatibleNamespace(namespace)

        self._namespace = namespace
        self._extractor = self.config_service.find_plugin(extractor_name, plugin_type=PluginType.EXTRACTORS)

        return self

    def with_loader(self, loader_name: str):
        self._loader = self.config_service.find_plugin(loader_name, plugin_type=PluginType.LOADERS)
        return self

    def plugin_config(self, session, plugin):
        return self.settings_service.as_config(session, plugin)

    def context(self, session) -> ELTContext:
        context = ELTContext(self.project,
                             self._loader,
                             extractor=self._extractor,
                             namespace=self._namespace)

        if self._extractor:
            context.extractor_config = self.plugin_config(session, self._extractor)

        if self._loader:
            context.loader_config = self.plugin_config(session, self._loader)

        return context
