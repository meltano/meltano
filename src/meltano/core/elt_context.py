"""ELT Context."""

from __future__ import annotations

import typing as t

from meltano.core._protocols.el_context import ELContextProtocol
from meltano.core._state import StateStrategy
from meltano.core.plugin import PluginRef, PluginType
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin_invoker import invoker_factory

if t.TYPE_CHECKING:
    import uuid
    from pathlib import Path

    from sqlalchemy.orm import Session

    from meltano.core.job import Job
    from meltano.core.logging.output_logger import OutputLogger
    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.plugin_invoker import PluginInvoker
    from meltano.core.project import Project


class PluginContext(t.NamedTuple):
    """Plugin Context container."""

    plugin: ProjectPlugin
    settings_service: PluginSettingsService
    session: Session

    def __getattr__(self, attr: str) -> t.Any:  # noqa: ANN401
        """Get plugin attribute.

        Args:
            attr: Attribute name.

        Returns:
            Attribute value.
        """
        return getattr(self.plugin, attr)

    def get_config(self, name: str, **kwargs: t.Any) -> t.Any:  # noqa: ANN401
        """Get plugin config by name.

        Args:
            name: Setting name to retrieve config for.
            kwargs: Keyword arguments to pass to SettingService.

        Returns:
            Setting value, if found, else None.
        """
        return self.settings_service.get(name, session=self.session, **kwargs)

    def config_dict(self, **kwargs) -> dict:  # noqa: ANN003
        """Get plugins config dict.

        Args:
            kwargs: Keyword arguments to pass to SettingService.

        Returns:
            Plugins config dict.
        """
        return self.settings_service.as_dict(session=self.session, **kwargs)

    def config_env(self, **kwargs) -> dict[str, str]:  # noqa: ANN003
        """Get plugins config environment.

        Args:
            kwargs: Keyword arguments to pass to SettingService.

        Returns:
            Plugins config environment dict.
        """
        return self.settings_service.as_env(session=self.session, **kwargs)

    @property
    def env(self) -> dict[str, str]:
        """Get complete plugin environment dict.

        Returns:
            Complete plugin environment dict.
        """
        return {**self.plugin.info_env, **self.config_env()}


class ELTContext(ELContextProtocol):
    """ELT Context."""

    def __init__(
        self,
        *,
        project: Project,
        job: Job | None = None,
        session=None,  # noqa: ANN001
        extractor: PluginContext | None = None,
        loader: PluginContext | None = None,
        transform: PluginContext | None = None,
        transformer: PluginContext | None = None,
        only_transform: bool | None = False,
        dry_run: bool | None = False,
        full_refresh: bool | None = False,
        refresh_catalog: bool | None = False,
        select_filter: list | None = None,
        catalog: str | None = None,
        state: str | None = None,
        base_output_logger: OutputLogger | None = None,
        state_strategy: StateStrategy = StateStrategy.auto,
        run_id: uuid.UUID | None = None,
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
            refresh_catalog: Flag. Ignore cached catalog.
            select_filter: Select filters to apply to extractor.
            catalog: Catalog to pass to extractor.
            state: State to pass to extractor.
            base_output_logger: OutputLogger to use.
            state_strategy: State strategy to use.
            run_id: Run ID.
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
        self.refresh_catalog = refresh_catalog
        self.select_filter = select_filter or []
        self.catalog = catalog
        self.state = state

        self.base_output_logger = base_output_logger
        self.state_strategy = state_strategy
        self.run_id = run_id

    @property
    def elt_run_dir(self) -> Path | None:
        """Get the ELT run directory.

        Returns:
            The job dir, if a Job is provided, else None.
        """
        if self.job:
            return self.project.job_dir(self.job.job_name, str(self.job.run_id))  # type: ignore[deprecated]

        return None

    def invoker_for(self, plugin_type: PluginType) -> PluginInvoker:
        """Get invoker for given plugin type.

        Args:
            plugin_type: Plugin type to get invoker for.

        Returns:
            A PluginInvoker.

        Raises:
            RuntimeError: If plugin context could not be found for the given plugin
                type.
        """
        plugin_contexts = {
            PluginType.EXTRACTORS: self.extractor,
            PluginType.LOADERS: self.loader,
            PluginType.TRANSFORMERS: self.transformer,
        }

        if plugin_context := plugin_contexts[plugin_type]:
            return invoker_factory(
                self.project,
                plugin_context.plugin,
                context=self,
                run_dir=self.elt_run_dir,
                plugin_settings_service=plugin_context.settings_service,
            )

        errmsg = f"Plugin context could not be found for {plugin_type.value}"  # pragma: no cover  # noqa: E501
        raise RuntimeError(errmsg)  # pragma: no cover

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


class ELTContextBuilder:
    """ELT Context Builder."""

    def __init__(self, project: Project):
        """Instantiate new ELTContextBuilder.

        Args:
            project: A Meltano Project instance.
        """
        self.project = project

        self._session: Session | None = None
        self._job: Job | None = None

        self._extractor: PluginRef | None = None
        self._loader: PluginRef | None = None
        self._transform: PluginRef | None = None
        self._transformer: PluginRef | None = None

        self._only_transform = False
        self._dry_run = False
        self._full_refresh = False
        self._refresh_catalog = False
        self._select_filter: list[str] | None = None
        self._catalog: str | None = None
        self._state: str | None = None
        self._base_output_logger: OutputLogger | None = None
        self._state_strategy: StateStrategy = StateStrategy.auto

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

    def with_only_transform(self, *, only_transform: bool) -> ELTContextBuilder:
        """Include only transform flag when building context.

        Args:
            only_transform: Flag. Only run transform.

        Returns:
            Updated ELTContextBuilder instance.
        """
        self._only_transform = only_transform
        return self

    def with_dry_run(self, *, dry_run: bool) -> ELTContextBuilder:
        """Include dry run flag when building context.

        Args:
            dry_run: Flag. Do not actually run.

        Returns:
            Updated ELTContextBuilder instance.
        """
        self._dry_run = dry_run
        return self

    def with_full_refresh(self, *, full_refresh: bool) -> ELTContextBuilder:
        """Include full refresh flag when building context.

        Args:
            full_refresh: Whether to perform a full refresh (ignore state left
                behind by any previous runs).

        Returns:
            Updated ELTContextBuilder instance.
        """
        self._full_refresh = full_refresh
        return self

    def with_refresh_catalog(self, *, refresh_catalog: bool) -> ELTContextBuilder:
        """Ignore cached catalog.

        Args:
            refresh_catalog: Whether ignore cached catalog.

        Returns:
            Updated ELTContextBuilder instance.
        """
        self._refresh_catalog = refresh_catalog
        return self

    def with_state_strategy(self, *, state_strategy: StateStrategy):  # noqa: ANN201
        """Set whether the state is to be merged or overwritten.

        Args:
            state_strategy: State strategy to use.

        Returns:
            Updated ELTContextBuilder instance.
        """
        self._state_strategy = state_strategy
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

    def with_catalog(self, catalog: str | None) -> ELTContextBuilder:
        """Include catalog file path when building context.

        Args:
            catalog: Path to singer catalog file.

        Returns:
            Updated ELTContextBuilder instance.
        """
        self._catalog = catalog
        return self

    def with_state(self, state: str | None) -> ELTContextBuilder:
        """Include state file path when building context.

        Args:
            state: Path to a singer state file.

        Returns:
            Updated ELTContextBuilder instance.
        """
        self._state = state
        return self

    def with_run_id(self, run_id: uuid.UUID | None) -> ELTContextBuilder:
        """Set a run ID for this run.

        Args:
            run_id: The run ID value.

        Returns:
            self
        """
        self._run_id = run_id
        return self

    def set_base_output_logger(self, base_output_logger: OutputLogger) -> None:
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
            plugin = self.project.plugins.get_plugin(plugin_ref)
        except PluginNotFoundError as err:
            if plugin_ref.name == "dbt":
                raise PluginNotFoundError(  # noqa: TRY003
                    "Transformer 'dbt' not found.\n"  # noqa: EM101
                    "Use of the legacy 'dbt' Transformer is deprecated in favor of "
                    "new adapter specific implementations (e.g. 'dbt-snowflake') "
                    "compatible with the 'meltano run ...' command.\n"
                    "https://docs.meltano.com/guide/transformation\n"
                    "To continue using the legacy 'dbt' Transformer, "
                    "add it to your Project using 'meltano add transformer dbt'.",
                ) from err
            raise

        return PluginContext(
            plugin=plugin,
            settings_service=PluginSettingsService(
                self.project,
                plugin,
                env_override=env,
                config_override=config,
            ),
            session=self._session,  # type: ignore[arg-type]
        )

    def context(self) -> ELTContext:
        """Return ELT context.

        Returns:
            ELTContext instance.
        """
        env: dict[str, str] = {}

        extractor = None
        if self._extractor:
            config: dict[str, t.Any] = {}
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

            env |= extractor.env

        loader = None
        if self._loader:
            loader = self.plugin_context(
                self._loader,
                env=env.copy(),
            )

            env |= loader.env

        transform = None
        if self._transform:
            transform = self.plugin_context(
                self._transform,
                env=env.copy(),
            )

            env |= transform.env

        transformer = None
        if self._transformer:
            transformer = self.plugin_context(
                self._transformer,
                env=env.copy(),
            )

        return ELTContext(
            project=self.project,
            job=self._job,
            session=self._session,
            extractor=extractor,
            loader=loader,
            transform=transform,
            transformer=transformer,
            only_transform=self._only_transform,
            dry_run=self._dry_run,
            full_refresh=self._full_refresh,
            refresh_catalog=self._refresh_catalog,
            select_filter=self._select_filter,
            catalog=self._catalog,
            state=self._state,
            base_output_logger=self._base_output_logger,
            state_strategy=self._state_strategy,
        )
