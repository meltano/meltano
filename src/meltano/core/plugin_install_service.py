"""Install plugins into the project, using pip in separate virtual environments by default."""


from __future__ import annotations

import asyncio
import functools
import logging
import os
import sys
from enum import Enum
from multiprocessing import cpu_count
from typing import Any, Callable, Iterable, Mapping

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

from cached_property import cached_property

from meltano.core.error import (
    AsyncSubprocessError,
    PluginInstallError,
    PluginInstallWarning,
)
from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.settings_service import FeatureFlags
from meltano.core.utils import EnvVarMissingBehavior, expand_env_vars, noop
from meltano.core.venv_service import VenvService

logger = logging.getLogger(__name__)


class PluginInstallReason(str, Enum):
    """Plugin install reason enum."""

    ADD = "add"
    INSTALL = "install"
    UPGRADE = "upgrade"


class PluginInstallStatus(Enum):
    """The status of the process of installing a plugin."""

    RUNNING = "running"
    SUCCESS = "success"
    SKIPPED = "skipped"
    ERROR = "error"
    WARNING = "warning"


class PluginInstallState:
    """A message reporting the progress of installing a plugin."""

    def __init__(
        self,
        plugin: ProjectPlugin,
        reason: PluginInstallReason,
        status: PluginInstallStatus,
        message: str | None = None,
        details: str | None = None,
    ):
        """Initialize PluginInstallState instance.

        Args:
            plugin: Plugin related to this install state.
            reason: Reason for plugin install.
            status: Status of plugin install.
            message: Formatted install state message.
            details: Extra details relating to install (including error details if failed).
        """
        # TODO: use dataclasses.dataclass for this when 3.6 support is dropped
        self.plugin = plugin
        self.reason = reason
        self.status = status
        self.message = message
        self.details = details

    @property
    def successful(self):
        """Plugin install success status.

        Returns:
            'True' if plugin install successful.
        """
        return self.status in {PluginInstallStatus.SUCCESS, PluginInstallStatus.SKIPPED}

    @property
    def skipped(self):
        """Plugin install skipped status.

        Returns:
            'True' if the installation was skipped / not needed.
        """
        return self.status == PluginInstallStatus.SKIPPED

    @property
    def verb(self) -> str:
        """Verb form of status.

        Returns:
            Verb form of status.
        """
        if self.status is PluginInstallStatus.RUNNING:
            return (
                "Updating"
                if self.reason is PluginInstallReason.UPGRADE
                else "Installing"
            )
        if self.status is PluginInstallStatus.SUCCESS:
            return (
                "Updated" if self.reason is PluginInstallReason.UPGRADE else "Installed"
            )
        if self.status is PluginInstallStatus.SKIPPED:
            return "Skipped installing"

        return "Errored"


def with_semaphore(func):
    """Gate access to the method using its class's semaphore.

    Args:
        func: Function to wrap.

    Returns:
        Wrapped function.
    """

    @functools.wraps(func)  # noqa: WPS430
    async def wrapper(self, *args, **kwargs):  # noqa: WPS430
        async with self.semaphore:
            return await func(self, *args, **kwargs)

    return wrapper


class PluginInstallService:  # noqa: WPS214
    """Plugin install service."""

    def __init__(
        self,
        project: Project,
        plugins_service: ProjectPluginsService | None = None,
        status_cb: Callable[[PluginInstallState], Any] = noop,
        parallelism: int | None = None,
        clean: bool = False,
        force: bool = False,
    ):
        """Initialize new PluginInstallService instance.

        Args:
            project: Meltano Project.
            plugins_service: Project plugins service to use.
            status_cb: Status call-back function.
            parallelism: Number of parallel installation processes to use.
            clean: Clean install flag.
            force: Whether to ignore the Python version required by plugins.
        """
        self.project = project
        self.plugins_service = plugins_service or ProjectPluginsService(project)
        self.status_cb = status_cb
        if parallelism is None:
            self.parallelism = cpu_count()
        elif parallelism < 1:
            self.parallelism = sys.maxsize
        self.clean = clean
        self.force = force

    @cached_property
    def semaphore(self):
        """An asyncio semaphore with a counter starting at `self.parallelism`.

        Returns:
            An asyncio semaphore with a counter starting at `self.parallelism`.
        """  # noqa: D401
        return asyncio.Semaphore(self.parallelism)

    @staticmethod
    def remove_duplicates(
        plugins: Iterable[ProjectPlugin], reason: PluginInstallReason
    ):
        """Deduplicate list of plugins, keeping the last occurrences.

        Trying to install multiple plugins into the same venv via `asyncio.run` will fail
        due to a race condition between the duplicate installs. This is particularly
        problematic if `clean` is set as one async `clean` operation causes the other
        install to fail.

        Args:
            plugins: An iterable containing plugins to dedupe.
            reason: Plugins install reason.

        Returns:
            A tuple containing a list of PluginInstallState instance (for skipped plugins)
            and a deduplicated list of plugins to install.
        """
        seen_venvs = set()
        deduped_plugins = []
        states = []
        for plugin in plugins:
            if (plugin.type, plugin.venv_name) not in seen_venvs:
                deduped_plugins.append(plugin)
                seen_venvs.add((plugin.type, plugin.venv_name))
            else:
                states.append(
                    PluginInstallState(
                        plugin=plugin,
                        reason=reason,
                        status=PluginInstallStatus.SKIPPED,
                        message=(
                            f"Plugin {plugin.name!r} does not require "
                            "installation: reusing parent virtualenv"
                        ),
                    )
                )
        return states, deduped_plugins

    def install_all_plugins(
        self, reason=PluginInstallReason.INSTALL
    ) -> tuple[PluginInstallState]:
        """
        Install all the plugins for the project.

        Blocks until all plugins are installed.

        Args:
            reason: Plugin install reason.

        Returns:
            Install state of installed plugins.
        """
        return self.install_plugins(self.plugins_service.plugins(), reason=reason)

    def install_plugins(
        self,
        plugins: Iterable[ProjectPlugin],
        reason=PluginInstallReason.INSTALL,
    ) -> tuple[PluginInstallState]:
        """
        Install all the provided plugins.

        Blocks until all plugins are installed.

        Args:
            plugins: ProjectPlugin instances to install.
            reason: Plugin install reason.

        Returns:
            Install state of installed plugins.
        """
        states, new_plugins = self.remove_duplicates(plugins=plugins, reason=reason)
        for state in states:
            self.status_cb(state)
        states.extend(
            asyncio.run(self.install_plugins_async(new_plugins, reason=reason))
        )
        return states

    async def install_plugins_async(
        self,
        plugins: Iterable[ProjectPlugin],
        reason=PluginInstallReason.INSTALL,
    ) -> tuple[PluginInstallState]:
        """Install all the provided plugins.

        Args:
            plugins: ProjectPlugin instances to install.
            reason: Plugin install reason.

        Returns:
            Install state of installed plugins.
        """
        return await asyncio.gather(
            *[self.install_plugin_async(plugin, reason) for plugin in plugins]
        )

    def install_plugin(
        self,
        plugin: ProjectPlugin,
        reason=PluginInstallReason.INSTALL,
    ) -> PluginInstallState:
        """
        Install a plugin.

        Blocks until the plugin is installed.

        Args:
            plugin: ProjectPlugin to install.
            reason: Install reason.

        Returns:
            PluginInstallState state instance.
        """
        return asyncio.run(
            self.install_plugin_async(
                plugin,
                reason=reason,
            )
        )

    @with_semaphore
    async def install_plugin_async(
        self,
        plugin: ProjectPlugin,
        reason=PluginInstallReason.INSTALL,
    ) -> PluginInstallState:
        """Install a plugin asynchronously.

        Args:
            plugin: ProjectPlugin to install.
            reason: Install reason.

        Returns:
            PluginInstallState state instance.
        """
        self.status_cb(
            PluginInstallState(
                plugin=plugin,
                reason=reason,
                status=PluginInstallStatus.RUNNING,
            )
        )

        if not plugin.is_installable() or self._is_mapping(plugin):
            state = PluginInstallState(
                plugin=plugin,
                reason=reason,
                status=PluginInstallStatus.SKIPPED,
                message=f"Plugin '{plugin.name}' does not require installation",
            )
            self.status_cb(state)
            return state

        try:
            async with plugin.trigger_hooks("install", self, plugin, reason):
                installer: PluginInstaller = getattr(
                    plugin, "installer", install_pip_plugin
                )
                await installer(
                    project=self.project,
                    plugin=plugin,
                    reason=reason,
                    clean=self.clean,
                    force=self.force,
                    env=self.plugin_installation_env(plugin),
                )
                state = PluginInstallState(
                    plugin=plugin, reason=reason, status=PluginInstallStatus.SUCCESS
                )
                self.status_cb(state)
                return state

        except PluginInstallError as err:
            state = PluginInstallState(
                plugin=plugin,
                reason=reason,
                status=PluginInstallStatus.ERROR,
                message=str(err),
            )
            self.status_cb(state)
            return state

        except PluginInstallWarning as warn:
            state = PluginInstallState(
                plugin=plugin,
                reason=reason,
                status=PluginInstallStatus.WARNING,
                message=str(warn),
            )
            self.status_cb(state)
            return state

        except AsyncSubprocessError as err:
            state = PluginInstallState(
                plugin=plugin,
                reason=reason,
                status=PluginInstallStatus.ERROR,
                message=(
                    f"{plugin.type.descriptor} '{plugin.name}' "
                    + f"could not be installed: {err}"
                ).capitalize(),
                details=await err.stderr,
            )
            self.status_cb(state)
            return state

    @staticmethod
    def _is_mapping(plugin: ProjectPlugin) -> bool:
        """Check if a plugin is a mapping, as mappings are not installed.

        Mappings are PluginType.MAPPERS with extra attribute of `_mapping` which will indicate
        that this instance of the plugin is actually a mapping - and should not be installed.

        Args:
            plugin: ProjectPlugin to evaluate.

        Returns:
            A boolean determining if the given plugin is a mapping (of type PluginType.MAPPERS).
        """
        return plugin.type == PluginType.MAPPERS and plugin.extra_config.get("_mapping")

    def plugin_installation_env(self, plugin: ProjectPlugin) -> dict[str, str]:
        """Environment variables to use during plugin installation.

        Args:
            plugin: The plugin being installed.

        Returns:
            A dictionary of environment variables from the process'
            environment, `meltano.yml`, the plugin `env` config, et cetera, in
            accordance with the normal Meltano env precedence hierarchy. See
            https://docs.meltano.com/guide/configuration#specifying-environment-variables.
            A special env var (with lowest precedence) `$MELTANO__PYTHON_VERSION`
            is included, and has the value
            `<major Python version>.<minor Python version>`.
        """
        project_settings_service = ProjectSettingsService(
            self.project, config_service=self.plugins_service.config_service
        )
        plugin_settings_service = PluginSettingsService(
            self.project, plugin, plugins_service=self.plugins_service
        )
        with project_settings_service.feature_flag(
            FeatureFlags.STRICT_ENV_VAR_MODE, raise_error=False
        ) as strict_env_var_mode:
            expanded_project_env = expand_env_vars(
                project_settings_service.env,
                os.environ,
                if_missing=EnvVarMissingBehavior(strict_env_var_mode),
            )
            return {
                "MELTANO__PYTHON_VERSION": f"{sys.version_info.major}.{sys.version_info.minor}",
                **expanded_project_env,
                **expand_env_vars(
                    plugin_settings_service.project.dotenv_env,
                    os.environ,
                    if_missing=EnvVarMissingBehavior(strict_env_var_mode),
                ),
                **plugin_settings_service.as_env(),
                **plugin_settings_service.plugin.info_env,
                **expand_env_vars(
                    plugin_settings_service.plugin.env,
                    expanded_project_env,
                    if_missing=EnvVarMissingBehavior(strict_env_var_mode),
                ),
            }


class PluginInstaller(Protocol):
    """Prototype function for plugin installation.

    All plugin installation functions must support at least the specified
    parameters, and also accept additional unused keyword arguments.
    """

    async def __call__(
        self,
        *,
        project: Project,
        plugin: ProjectPlugin,
        **kwargs,
    ) -> None:
        """Install the plugin.

        Args:
            project: Meltano Project.
            plugin: `ProjectPlugin` to install.
            kwargs: Additional arguments for the installation of the plugin.
        """


async def install_pip_plugin(
    *,
    project: Project,
    plugin: ProjectPlugin,
    clean: bool = False,
    force: bool = False,
    venv_service: VenvService | None = None,
    env: Mapping[str, str] | None = None,
    **kwargs,
):
    """Install the plugin with pip.

    Args:
        project: Meltano Project.
        plugin: `ProjectPlugin` to install.
        clean: Flag to clean install.
        force: Whether to ignore the Python version required by plugins.
        venv_service: `VenvService` instance to use when installing.
        env: Environment variables to use when expanding the pip install args.
        kwargs: Unused additional arguments for the installation of the plugin.
    """
    with ProjectSettingsService(project).feature_flag(
        FeatureFlags.STRICT_ENV_VAR_MODE, raise_error=False
    ) as strict_env_var_mode:
        pip_install_args = expand_env_vars(
            plugin.pip_url,
            env,
            if_missing=EnvVarMissingBehavior(strict_env_var_mode),
        ).split(" ")

    venv_service = venv_service or VenvService(
        project, namespace=plugin.type, name=plugin.venv_name
    )
    await venv_service.install(
        pip_install_args=["--ignore-requires-python", *pip_install_args]
        if force
        else pip_install_args,
        clean=clean,
    )
