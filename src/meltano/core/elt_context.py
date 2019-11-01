from typing import Optional
from collections import namedtuple

from meltano.core.project import Project
from meltano.core.job import Job
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
        self,
        project,
        loader: PluginContext,
        job: Optional[Job] = None,
        extractor: Optional[PluginContext] = None,
        plugin_settings_service: PluginSettingsService = None,
        plugin_discovery_service: PluginDiscoveryService = None,
    ):
        self.project = project
        self.job = job
        self.loader = loader
        self.extractor = extractor
        self.plugin_settings_service = plugin_settings_service
        self.plugin_discovery_service = (
            plugin_discovery_service or PluginDiscoveryService(project)
        )

    @property
    def elt_run_dir(self):
        if self.job:
            self.project.job_dir(self.job.job_id, str(self.job.run_id))

    def extractor_invoker(self):
        return invoker_factory(
            self.project,
            self.extractor.install,
            run_dir=self.elt_run_dir,
            plugin_config=self.extractor.config,
            plugin_settings_service=self.plugin_settings_service,
            plugin_discovery_service=self.plugin_discovery_service,
        )

    def loader_invoker(self):
        return invoker_factory(
            self.project,
            self.loader.install,
            run_dir=self.elt_run_dir,
            plugin_config=self.loader.config,
            plugin_settings_service=self.plugin_settings_service,
            plugin_discovery_service=self.plugin_discovery_service,
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
        self.plugin_discovery_service = (
            plugin_discovery_service
            or PluginDiscoveryService(project, config_service=config_service)
        )
        self.plugin_settings_service = plugin_settings_service or PluginSettingsService(
            project,
            config_service=config_service,
            plugin_discovery_service=plugin_discovery_service,
        )
        self._extractor = None
        self._loader = None
        self._job = None

    def with_extractor(self, extractor_name: str):
        self._extractor = PluginRef(PluginType.EXTRACTORS, extractor_name)

        return self

    def with_loader(self, loader_name: str):
        self._loader = PluginRef(PluginType.LOADERS, loader_name)

        return self

    def with_job(self, job: Job):
        self._job = job

        return self

    def plugin_context(self, session, plugin: PluginRef):
        return PluginContext(
            ref=plugin,
            install=self.config_service.find_plugin(
                plugin_name=plugin.name, plugin_type=plugin.type
            ),
            definition=self.plugin_discovery_service.find_plugin(
                plugin_name=plugin.name, plugin_type=plugin.type
            ),
            config=self.plugin_settings_service.as_config(session, plugin),
        )

    def context(self, session) -> ELTContext:
        return ELTContext(
            self.project,
            self.plugin_context(session, self._loader),
            job=self._job,
            extractor=self.plugin_context(session, self._extractor)
            if self._extractor
            else None,
            plugin_settings_service=self.plugin_settings_service,
            plugin_discovery_service=self.plugin_discovery_service,
        )
