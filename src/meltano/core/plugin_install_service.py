"""Install plugins into the project, using pip in separate virtual environments by default."""


from __future__ import annotations

import asyncio
import contextlib
import functools
import logging
import sys
from enum import Enum
from multiprocessing import cpu_count
from typing import Any, Callable, Iterable

from cached_property import cached_property

from meltano.core.error import (
    AsyncSubprocessError,
    PluginInstallError,
    PluginInstallWarning,
)
from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.utils import noop
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


def installer_factory(project, plugin: ProjectPlugin, *args, **kwargs):
    """Installer Factory.

    Args:
        project: Meltano Project.
        plugin: Plugin to be installed.
        args: Positional arguments to instantiate installer with.
        kwargs: Keyword arguments to instantiate installer with.

    Returns:
        An instantiated plugin installer for the given plugin.
    """
    installer_class = PipPluginInstaller
    with contextlib.suppress(AttributeError):
        installer_class = plugin.installer_class
    return installer_class(project, plugin, *args, **kwargs)


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
                await installer_factory(self.project, plugin).install(
                    reason=reason,
                    clean=self.clean,
                    force=self.force,
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


class PipPluginInstaller:
    """Plugin installer for pip-based plugins."""

    def __init__(
        self,
        project,
        plugin: ProjectPlugin,
        venv_service: VenvService | None = None,
    ):
        """Initialize PipPluginInstaller instance.

        Args:
            project: Meltano Project.
            plugin: ProjectPlugin to install.
            venv_service: VenvService instance to use when installing.
        """
        self.plugin = plugin
        self.venv_service = venv_service or VenvService(
            project,
            namespace=self.plugin.type,
            name=self.plugin.venv_name,
        )

    async def install(
        self, reason: PluginInstallReason, clean: bool, force: bool
    ) -> None:
        """Install the plugin into the virtual environment using pip.

        Args:
            reason: Install reason.
            clean: Flag to clean install.
            force: Whether to ignore the Python version required by plugins.
        """
        pip_install_args = self.plugin.formatted_pip_url.split(" ")
        if force:
            pip_install_args.insert(0, "--ignore-requires-python")
        await self.venv_service.install(
            pip_install_args=pip_install_args,
            clean=clean,
        )
