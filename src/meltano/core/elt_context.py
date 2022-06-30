"""ELT Context."""

from __future__ import annotations

from collections import namedtuple
from typing import Any

from sqlalchemy.orm import Session

from meltano.core.job import Job
from meltano.core.logging.output_logger import OutputLogger
from meltano.core.plugin import PluginRef, PluginType
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin_invoker import PluginInvoker, invoker_factory
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService


class PluginContext(
    namedtuple("PluginContext", "plugin settings_service session")  # noqa: WPS606
):
    """Plugin Context container."""

    def __getattr__(self, attr: str) -> Any:
        """Get plugin attribute.

        Args:
            attr: Attribute name.

        Returns:
            Attribute value.
        """
        return getattr(self.plugin, attr)

    def get_config(self, name: str, **kwargs: Any) -> Any:
        """Get plugin config by name.

        Args:
            name: Setting name to retrieve config for.
            kwargs: Keyword arguments to pass to SettingService.

        Returns:
            Setting value, if found, else None.
        """
        return self.settings_service.get(name, session=self.session, **kwargs)

    def config_dict(self, **kwargs) -> dict:
        """Get plugins config dict.

        Args:
            kwargs: Keyword arguments to pass to SettingService.

        Returns:
            Plugins config dict.
        """
        return self.settings_service.as_dict(session=self.session, **kwargs)

    def config_env(self, **kwargs) -> dict[str, str]:
        """Get plugins config environment.

        Args:
            kwargs: Keyword arguments to pass to SettingService.

        Returns:
            Plugins config environment dict.
        """
        return self.settings_service.as_env(session=self.session, **kwargs)

    @property
    def env(self) -> dict:
        """Get complete plugin environment dict.

        Returns:
            Complete plugin environment dict.
        """
        return {**self.plugin.info_env, **self.config_env()}


class ELTContext:  # noqa: WPS230
    """ELT Context."""

    def __init__(
        self,
        project,
        job: Job | None = None,
        session=None,
        extractor: PluginContext | None = None,
        loader: PluginContext | None = None,
        transform: PluginContext | None = None,
        transformer: PluginContext | None = None,
        only_transform: bool | None = False,
        dry_run: bool | None = False,
        full_refresh: bool | None = False,
        select_filter: list | None = None,
        catalog: str | None = None,
        state: str | None = None,
        plugins_service: ProjectPluginsService = None,
        base_output_logger: OutputLogger | None = None,
    ):
        """Initialise ELT Context instance.

        Args:
            project: Meltano Project instance.
            job: Job instance.
            session: SQLAlchemy Session instance.
            extractor: Extractor to use.
            loader: Loader to use.
            transform: Transform to use.
            transformer: Transformer to use.
            only_transform: Flag. Only run transform.
            dry_run: Flag. Don't actually run.
            full_refresh: Flag. Ignore previous captured state.
            select_filter: Select filters to apply to extractor.
            catalog: Catalog to pass to extractor.
            state: State to pass to extractor.
            plugins_service: PluginsService to use.
            base_output_logger: OutputLogger to use.
        """
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
        self.select_filter = select_filter or []
        self.catalog = catalog
        self.state = state

        self.plugins_service = plugins_service or ProjectPluginsService(project)
        self.base_output_logger = base_output_logger

    @property
    def elt_run_dir(self):
        """Get the ELT run directory.

        Returns:
            The job dir, if a Job is provided, else None.
        """
        if self.job:
            return self.project.job_dir(self.job.job_name, str(self.job.run_id))

    def invoker_for(self, plugin_type: PluginType) -> PluginInvoker:
        """Get invoker for given plugin type.

        Args:
            plugin_type: Plugin type to get invoker for.

        Returns:
            A PluginInvoker.
        """
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

    def extractor_invoker(self) -> PluginInvoker:
        """Get the extractors' invoker.

        Returns:
            Invoker for contexts transformer.
        """
        return self.invoker_for(PluginType.EXTRACTORS)

    def loader_invoker(self) -> PluginInvoker:
        """Get the loaders' invoker.

        Returns:
            Invoker for contexts loader.
        """
        return self.invoker_for(PluginType.LOADERS)

    def transformer_invoker(self) -> PluginInvoker:
        """Get the transformers' invoker.

        Returns:
            Invoker for contexts transformer.
        """
        return self.invoker_for(PluginType.TRANSFORMERS)


class ELTContextBuilder:  # noqa: WPS214
    """ELT Context Builder."""

    def __init__(
        self,
        project: Project,
        plugins_service: ProjectPluginsService = None,
    ):
        """Instantiate new ELTContextBuilder.

        Args:
            project: A Meltano Project instance.
            plugins_service: A PluginsService instance.
        """
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

    def with_session(self, session: Session) -> ELTContextBuilder:
        """Include session when building context.

        Args:
            session: A SQLAlchemy session.

        Returns:
            Updated ELTContextBuilder instance.
        """
        self._session = session
        return self

    def with_job(self, job: Job) -> ELTContextBuilder:
        """Include job when building context.

        Args:
            job: Job instance.

        Returns:
            Updated ELTContextBuilder instance.
        """
        self._job = job
        return self

    def with_extractor(self, extractor_name: str) -> ELTContextBuilder:
        """Include extractor when building context.

        Args:
            extractor_name: Extractor name.

        Returns:
            Updated ELTContextBuilder instance.
        """
        self._extractor = PluginRef(PluginType.EXTRACTORS, extractor_name)
        return self

    def with_loader(self, loader_name: str) -> ELTContextBuilder:
        """Include loader when building context.

        Args:
            loader_name: Loader name.

        Returns:
            Updated ELTContextBuilder instance.
        """
        self._loader = PluginRef(PluginType.LOADERS, loader_name)
        return self

    def with_transform(self, transform: str) -> ELTContextBuilder:
        """Include transform when building context.

        Args:
            transform: Choice of "skip", "only" or "run".

        Returns:
            Updated ELTContextBuilder instance.
        """
        if transform == "skip":
            return self

        if transform not in {"run", "only"}:
            self._transform = PluginRef(PluginType.TRANSFORMS, transform)

        return self.with_transformer("dbt")

    def with_transformer(self, transformer_name: str) -> ELTContextBuilder:
        """Include transformer when building context.

        Args:
            transformer_name: Name of transformer.

        Returns:
            Updated ELTContextBuilder instance.
        """
        self._transformer = PluginRef(PluginType.TRANSFORMERS, transformer_name)
        return self

    def with_only_transform(self, only_transform: bool) -> ELTContextBuilder:
        """Include only transform flag when building context.

        Args:
            only_transform: Flag. Only run transform.

        Returns:
            Updated ELTContextBuilder instance.
        """
        self._only_transform = only_transform
        return self

    def with_dry_run(self, dry_run: bool) -> ELTContextBuilder:
        """Include dry run flag when building context.

        Args:
            dry_run: Flag. Do not actually run.

        Returns:
            Updated ELTContextBuilder instance.
        """
        self._dry_run = dry_run
        return self

    def with_full_refresh(self, full_refresh: bool) -> ELTContextBuilder:
        """Include full refresh flag when building context.

        Args:
            full_refresh: Flag. Perform a full refresh (ignore state left behind by any previous runs).

        Returns:
            Updated ELTContextBuilder instance.
        """
        self._full_refresh = full_refresh
        return self

    def with_select_filter(self, select_filter: list[str]) -> ELTContextBuilder:
        """Include select filters when building context.

        Args:
            select_filter: A list of select filter strings.

        Returns:
            Updated ELTContextBuilder instance.
        """
        self._select_filter = select_filter
        return self

    def with_catalog(self, catalog: str) -> ELTContextBuilder:
        """Include catalog file path when building context.

        Args:
            catalog: Path to singer catalog file.

        Returns:
            Updated ELTContextBuilder instance.
        """
        self._catalog = catalog
        return self

    def with_state(self, state: str) -> ELTContextBuilder:
        """Include state file path when building context.

        Args:
            state: Path to a singer state file.

        Returns:
            Updated ELTContextBuilder instance.
        """
        self._state = state
        return self

    def set_base_output_logger(self, base_output_logger: OutputLogger):  # noqa: WPS615
        """Set the base output logger for use in this ELTContext.

        Args:
            base_output_logger: The OutputLogger to use.
        """
        self._base_output_logger = base_output_logger

    def plugin_context(
        self,
        plugin_ref: PluginRef,
        env: dict | None = None,
        config: dict | None = None,
    ) -> PluginContext:
        """Create context object for a plugin.

        Args:
            plugin_ref: Plugin reference object.
            env: Environment override dictionary.
            config: Plugin configuration override dictionary.

        Returns:
            A new `PluginContext` object.

        Raises:
            PluginNotFoundError: if a plugin specified cannot be found.
        """
        try:
            plugin = self.plugins_service.get_plugin(plugin_ref)
        except PluginNotFoundError as err:
            if plugin_ref.name == "dbt":
                raise PluginNotFoundError(
                    "Transformer 'dbt' not found.\n"
                    + "Use of the legacy 'dbt' Transformer is deprecated in favor of "
                    + "new adapter specific implementations (e.g. 'dbt-snowflake') "
                    + "compatible with the 'meltano run ...' command.\n"
                    + "https://docs.meltano.com/guide/transformation\n"
                    + "To continue using the legacy 'dbt' Transformer, "
                    + "add it to your Project using 'meltano add transformer dbt'."
                ) from err
            raise

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
        """Return ELT context.

        Returns:
            ELTContext instance.
        """
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
