from collections import namedtuple
from typing import Optional

from meltano.core.job import Job
from meltano.core.logging.output_logger import OutputLogger
from meltano.core.plugin import PluginRef, PluginType
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin_invoker import invoker_factory
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService


class PluginContext(namedtuple("PluginContext", "plugin settings_service session")):
    def __getattr__(self, attr):
        return getattr(self.plugin, attr)

    def get_config(self, name, **kwargs):
        return self.settings_service.get(name, session=self.session, **kwargs)

    def config_dict(self, **kwargs):
        return self.settings_service.as_dict(session=self.session, **kwargs)

    def config_env(self, **kwargs):
        return self.settings_service.as_env(session=self.session, **kwargs)

    @property
    def env(self):
        return {**self.plugin.info_env, **self.config_env()}


class ELTContext:
    def __init__(
        self,
        project,
        job: Optional[Job] = None,
        session=None,
        extractor: Optional[PluginContext] = None,
        loader: Optional[PluginContext] = None,
        transform: Optional[PluginContext] = None,
        transformer: Optional[PluginContext] = None,
        only_transform: Optional[bool] = False,
        dry_run: Optional[bool] = False,
        full_refresh: Optional[bool] = False,
        select_filter: Optional[list] = [],
        catalog: Optional[str] = None,
        state: Optional[str] = None,
        plugins_service: ProjectPluginsService = None,
        base_output_logger: Optional[OutputLogger] = None,
    ):
        self.project = project
        self.job = job
        self.session = session

        self.extractor = extractor
        self.loader = loader
        self.transform = transform
        self.transformer = transformer

        self.only_transform = only_transform
        self.dry_run = dry_run
        self.full_refresh = full_refresh
        self.select_filter = select_filter
        self.catalog = catalog
        self.state = state

        self.plugins_service = plugins_service or ProjectPluginsService(project)
        self.base_output_logger = base_output_logger

    @property
    def elt_run_dir(self):
        if self.job:
            return self.project.job_dir(self.job.job_id, str(self.job.run_id))

    def invoker_for(self, plugin_type):
        plugin_contexts = {
            PluginType.EXTRACTORS: self.extractor,
            PluginType.LOADERS: self.loader,
            PluginType.TRANSFORMERS: self.transformer,
        }

        plugin_context = plugin_contexts[plugin_type]
        return invoker_factory(
            self.project,
            plugin_context.plugin,
            context=self,
            run_dir=self.elt_run_dir,
            plugins_service=self.plugins_service,
            plugin_settings_service=plugin_context.settings_service,
        )

    def extractor_invoker(self):
        return self.invoker_for(PluginType.EXTRACTORS)

    def loader_invoker(self):
        return self.invoker_for(PluginType.LOADERS)

    def transformer_invoker(self):
        return self.invoker_for(PluginType.TRANSFORMERS)


class ELTContextBuilder:
    def __init__(
        self,
        project: Project,
        plugins_service: ProjectPluginsService = None,
    ):
        self.project = project
        self.plugins_service = plugins_service or ProjectPluginsService(project)

        self._session = None
        self._job = None

        self._extractor = None
        self._loader = None
        self._transform = None
        self._transformer = None

        self._only_transform = False
        self._dry_run = False
        self._full_refresh = False
        self._select_filter = None
        self._catalog = None
        self._state = None
        self._base_output_logger = None

    def with_session(self, session):
        self._session = session

        return self

    def with_job(self, job: Job):
        self._job = job

        return self

    def with_extractor(self, extractor_name: str):
        self._extractor = PluginRef(PluginType.EXTRACTORS, extractor_name)

        return self

    def with_loader(self, loader_name: str):
        self._loader = PluginRef(PluginType.LOADERS, loader_name)

        return self

    def with_transform(self, transform: str):
        if transform == "skip":
            return self

        if transform not in ("run", "only"):
            self._transform = PluginRef(PluginType.TRANSFORMS, transform)

        return self.with_transformer("dbt")

    def with_transformer(self, transformer_name: str):
        self._transformer = PluginRef(PluginType.TRANSFORMERS, transformer_name)

        return self

    def with_only_transform(self, only_transform):
        self._only_transform = only_transform

        return self

    def with_dry_run(self, dry_run):
        self._dry_run = dry_run

        return self

    def with_full_refresh(self, full_refresh):
        self._full_refresh = full_refresh

        return self

    def with_select_filter(self, select_filter):
        self._select_filter = select_filter

        return self

    def with_catalog(self, catalog):
        self._catalog = catalog

        return self

    def with_state(self, state):
        self._state = state

        return self

    def set_base_output_logger(self, base_output_logger: OutputLogger):
        """Set the base output logger for use in this ELTContext.

        Args:
            base_output_logger: The OutputLogger to use.
        """
        self._base_output_logger = base_output_logger

    def plugin_context(
        self,
        plugin_ref: PluginRef,
        env: dict = None,
        config: dict = None,
    ) -> PluginContext:
        """Create context object for a plugin.

        Args:
            plugin_ref: Plugin reference object.
            env: Environment override dictionary. Defaults to None.
            config: Plugin configuration override dictionary. Defaults to None.

        Returns:
            A new `PluginContext` object.
        """
        plugin = self.plugins_service.get_plugin(plugin_ref)

        return PluginContext(
            plugin=plugin,
            settings_service=PluginSettingsService(
                self.project,
                plugin,
                plugins_service=self.plugins_service,
                env_override=env,
                config_override=config,
            ),
            session=self._session,
        )

    def context(self) -> ELTContext:
        env = {}

        extractor = None
        if self._extractor:
            config = {}
            if self._select_filter:
                config["_select_filter"] = self._select_filter
            if self._catalog:
                config["_catalog"] = self._catalog
            if self._state:
                config["_state"] = self._state

            extractor = self.plugin_context(
                self._extractor,
                config=config,
            )

            env.update(extractor.env)

        loader = None
        if self._loader:
            loader = self.plugin_context(
                self._loader,
                env=env.copy(),
            )

            env.update(loader.env)

        transform = None
        if self._transform:
            transform = self.plugin_context(
                self._transform,
                env=env.copy(),
            )

            env.update(transform.env)

        transformer = None
        if self._transformer:
            transformer = self.plugin_context(
                self._transformer,
                env=env.copy(),
            )

        return ELTContext(
            self.project,
            job=self._job,
            session=self._session,
            extractor=extractor,
            loader=loader,
            transform=transform,
            transformer=transformer,
            only_transform=self._only_transform,
            dry_run=self._dry_run,
            full_refresh=self._full_refresh,
            select_filter=self._select_filter,
            catalog=self._catalog,
            state=self._state,
            plugins_service=self.plugins_service,
            base_output_logger=self._base_output_logger,
        )
