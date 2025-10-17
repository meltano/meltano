"""Module for working with meltano.yml files."""

from __future__ import annotations

import copy
import typing as t
import warnings

from meltano.core.behavior.canonical import Canonical
from meltano.core.environment import Environment
from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.schedule import ELTSchedule, JobSchedule
from meltano.core.task_sets import TaskSets

if t.TYPE_CHECKING:
    from collections.abc import Iterable

    from meltano.core.schedule import Schedule

VERSION = 1
_VERSION_SENTINEL = object()


class MeltanoFile(Canonical):
    """Data and loading methods for meltano.yml files."""

    version: int
    requires_meltano: str | None
    plugins: dict[PluginType, list[ProjectPlugin]]
    schedules: list[Schedule]
    environments: list[Environment]
    jobs: list[TaskSets]
    env: dict[str, str | None]
    extras: dict[str, t.Any]

    def __init__(
        self,
        version: int | object = _VERSION_SENTINEL,
        plugins: dict[str, dict] | None = None,
        schedules: list[dict] | None = None,
        environments: list[dict] | None = None,
        jobs: list[dict] | None = None,
        env: dict[str, str] | None = None,
        *,
        requires_meltano: str | None = None,
        **extras: t.Any,
    ):
        """Construct a new MeltanoFile object from meltano.yml file.

        Args:
            version: The meltano.yml version, currently always 1. (Deprecated)
            requires_meltano: The version of Meltano required by this project.
            plugins: Plugin configuration for this project.
            schedules: Schedule configuration for this project.
            environments: Environment configuration for this project.
            jobs: Job configuration for this project.
            env: Environment variables for this project.
            extras: Additional configuration for this project.
        """
        # Track whether version was explicitly provided
        self._version_explicitly_provided = version is not _VERSION_SENTINEL

        # Warn if version was explicitly provided in meltano.yml
        if version is not _VERSION_SENTINEL:
            warnings.warn(
                "The 'version' field in meltano.yml is deprecated and will be "
                "removed in a future release. Please remove it from your "
                "meltano.yml file. To specify Meltano version requirements, "
                "use 'requires_meltano' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
        else:
            # Use the default version if not provided
            version = VERSION

        super().__init__(
            # Attributes will be listed in meltano.yml in this order:
            version=version,
            extras=extras,
            plugins=self.load_plugins(plugins or {}),
            schedules=self.load_schedules(schedules or []),
            environments=self.load_environments(environments or []),
            jobs=self.load_job_tasks(jobs or []),
            env=self.load_env(env or {}),
            requires_meltano=requires_meltano,
        )

    def load_plugins(self, plugins: dict[str, dict]) -> Canonical:
        """Parse the `meltano.yml` file and return it as `ProjectPlugin` instances.

        Args:
            plugins: Dictionary of plugin configurations.

        Returns:
            New ProjectPlugin instances.
        """
        plugin_type_plugins = Canonical()

        for ptype in PluginType:
            plugin_type_plugins[ptype] = []

        # this will parse the meltano.yml file and create an instance of the
        # corresponding `plugin_class` for all the plugins.
        for plugin_type, raw_plugins in plugins.items():
            if plugin_type == PluginType.MAPPERS:
                for mapper in raw_plugins:
                    plugin_type_plugins[PluginType.MAPPERS].append(
                        ProjectPlugin(PluginType.MAPPERS, **mapper),
                    )
                    plugin_type_plugins[PluginType.MAPPERS].extend(
                        self.get_plugins_for_mappings(mapper),
                    )
            else:
                for raw_plugin in raw_plugins:
                    plugin = ProjectPlugin(PluginType(plugin_type), **raw_plugin)
                    plugin_type_plugins[plugin.type].append(plugin)

        return plugin_type_plugins

    def load_schedules(self, schedules: list[dict]) -> list[Schedule]:
        """Parse the meltano.yml file and return it as Schedule instances.

        Args:
            schedules: List of schedule configurations.

        Returns:
            List of new Schedule instances.
        """
        result: list[Schedule] = []
        for schedule in schedules:
            if schedule.get("job"):
                result.append(JobSchedule(**schedule))
            else:
                result.append(ELTSchedule(**schedule))
        return result

    def __iter__(self):  # noqa: ANN204
        """Return an iterator over the attributes.

        Excludes version if not explicitly provided.

        Yields:
            An iterator over the attributes set on the current instance.
        """
        for key, val in super().__iter__():
            # Skip version field if it wasn't explicitly provided
            if key == "version" and not self._version_explicitly_provided:
                continue
            yield (key, val)

    @staticmethod
    def load_environments(environments: Iterable[dict]) -> list[Environment]:
        """Parse `Environment` objects from python objects.

        Args:
            environments: Sequence of environment dictionaries.

        Returns:
            A list of `Environment` objects.
        """
        return [Environment.parse(obj) for obj in environments]

    @staticmethod
    def load_job_tasks(jobs: Iterable[dict]) -> list[TaskSets]:
        """Parse `TaskSets` objects from python objects.

        Args:
            jobs: Sequence of job dictionaries.

        Returns:
            A list of `Job` objects.
        """
        return [TaskSets.parse(obj) for obj in jobs]

    @staticmethod
    def load_env(env: dict) -> dict[str, str | None]:
        """Parse `EnvVars` objects from python objects.

        Args:
            env: Dictionary of environment variables.

        Returns:
            A new `EnvVars` object.
        """
        return {
            str(key): str(value) if value is not None else None
            for key, value in env.items()
        }

    @staticmethod
    def get_plugins_for_mappings(mapper_config: dict) -> list[ProjectPlugin]:
        """Get plugins for mappings.

        Mapper plugins are a special case. They are not a single plugin, but
        actually a list of plugins generated from the mapping config defined
        within the mapper config.

        Args:
            mapper_config: The dict representation of a mapper config found in
                in `meltano.yml`.

        Returns:
            A list of `ProjectPlugin` instances.
        """
        mapping_plugins: list[ProjectPlugin] = []
        for mapping in mapper_config.get("mappings", []):
            raw_mapping_plugin = copy.deepcopy(mapper_config)
            raw_mapping_plugin["mapping"] = True
            raw_mapping_plugin["mapping_name"] = mapping.get("name")
            raw_mapping_plugin["config"] = mapping.get("config")
            mapping_plugins.append(
                ProjectPlugin(PluginType.MAPPERS, **raw_mapping_plugin),
            )
        return mapping_plugins
