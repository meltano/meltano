"""Install plugins into the project, using pip in separate venv by default."""

from __future__ import annotations

import asyncio
import functools
import os
import shlex
import sys
import typing as t
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from multiprocessing import cpu_count

import structlog

from meltano.core.error import (
    AsyncSubprocessError,
    PluginInstallError,
    PluginInstallWarning,
)
from meltano.core.plugin import PluginType
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.settings_service import FeatureFlags
from meltano.core.utils import (
    EnvironmentVariableNotSetError,
    EnvVarMissingBehavior,
    expand_env_vars,
    noop,
)
from meltano.core.venv_service import (
    UvVenvService,
    VenvService,
    VirtualEnv,
    fingerprint,
)

if t.TYPE_CHECKING:
    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project

logger = structlog.stdlib.get_logger(__name__)


class PluginInstallReason(str, Enum):
    """Plugin install reason enum."""

    ADD = "add"
    AUTO = "auto"
    INSTALL = "install"
    UPGRADE = "upgrade"


class PluginInstallStatus(Enum):
    """The status of the process of installing a plugin."""

    RUNNING = "running"
    SUCCESS = "success"
    SKIPPED = "skipped"
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class PluginInstallState:
    """A message reporting the progress of installing a plugin.

    plugin: Plugin related to this install state.
    reason: Reason for plugin install.
    status: Status of plugin install.
    message: Formatted install state message.
    details: Extra details relating to install (including error details if failed).
    """

    plugin: ProjectPlugin
    reason: PluginInstallReason
    status: PluginInstallStatus
    message: str | None = None
    details: str | None = None

    @cached_property
    def successful(self):  # noqa: ANN201
        """Plugin install success status.

        Returns:
            `True` if plugin install successful.
        """
        return self.status in {PluginInstallStatus.SUCCESS, PluginInstallStatus.SKIPPED}

    @cached_property
    def skipped(self):  # noqa: ANN201
        """Plugin install skipped status.

        Returns:
            `True` if the installation was skipped / not needed.
        """
        return self.status == PluginInstallStatus.SKIPPED

    @cached_property
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


def with_semaphore(func):  # noqa: ANN001, ANN201
    """Gate access to the method using its class's semaphore.

    Args:
        func: Function to wrap.

    Returns:
        Wrapped function.
    """

    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        async with self.semaphore:
            return await func(self, *args, **kwargs)

    return wrapper


class PluginInstallService:
    """Plugin install service."""

    def __init__(
        self,
        project: Project,
        status_cb: t.Callable[[PluginInstallState], t.Any] = noop,
        *,
        parallelism: int | None = None,
        clean: bool = False,
        force: bool = False,
    ):
        """Initialize new PluginInstallService instance.

        Args:
            project: Meltano Project.
            status_cb: Status call-back function.
            parallelism: Number of parallel installation processes to use.
            clean: Clean install flag.
            force: Whether to ignore the Python version required by plugins.
        """
        self.project = project
        self.status_cb = status_cb
        self._parallelism = parallelism
        self.clean = clean
        self.force = force

    @cached_property
    def parallelism(self) -> int:
        """Return the number of parallel installation processes to use.

        Returns:
            The number of parallel installation processes to use.
        """
        if self._parallelism is None:
            return cpu_count()
        if self._parallelism < 1:
            return sys.maxsize
        return self._parallelism

    @cached_property
    def semaphore(self):  # noqa: ANN201
        """An asyncio semaphore with a counter starting at `self.parallelism`.

        Returns:
            An asyncio semaphore with a counter starting at `self.parallelism`.
        """
        return asyncio.Semaphore(self.parallelism)

    @staticmethod
    def remove_duplicates(  # noqa: ANN205
        plugins: t.Iterable[ProjectPlugin],
        reason: PluginInstallReason,
    ):
        """Deduplicate list of plugins, keeping the last occurrences.

        Trying to install multiple plugins into the same venv via `asyncio.run`
        will fail due to a race condition between the duplicate installs. This
        is particularly problematic if `clean` is set as one async `clean`
        operation causes the other install to fail.

        Args:
            plugins: An iterable containing plugins to dedupe.
            reason: Plugins install reason.

        Returns:
            A tuple containing a list of PluginInstallState instance (for
            skipped plugins) and a deduplicated list of plugins to install.
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
                    ),
                )
        return states, deduped_plugins

    async def install_all_plugins(
        self,
        reason=PluginInstallReason.INSTALL,  # noqa: ANN001
    ) -> tuple[PluginInstallState]:
        """Install all the plugins for the project.

        Blocks until all plugins are installed.

        Args:
            reason: Plugin install reason.

        Returns:
            Install state of installed plugins.
        """
        return await self.install_plugins(self.project.plugins.plugins(), reason=reason)

    async def install_plugins(
        self,
        plugins: t.Iterable[ProjectPlugin],
        reason=PluginInstallReason.INSTALL,  # noqa: ANN001
    ) -> tuple[PluginInstallState]:
        """Install all the provided plugins.

        Args:
            plugins: ProjectPlugin instances to install.
            reason: Plugin install reason.

        Returns:
            Install state of installed plugins.
        """
        states, new_plugins = self.remove_duplicates(plugins=plugins, reason=reason)
        for state in states:
            self.status_cb(state)

        installing = [
            self.install_plugin_async(plugin, reason) for plugin in new_plugins
        ]

        states.extend(await asyncio.gather(*installing))
        return states

    def install_plugin(
        self,
        plugin: ProjectPlugin,
        reason=PluginInstallReason.INSTALL,  # noqa: ANN001
    ) -> PluginInstallState:
        """Install a plugin.

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
            ),
        )

    @with_semaphore
    async def install_plugin_async(
        self,
        plugin: ProjectPlugin,
        reason=PluginInstallReason.INSTALL,  # noqa: ANN001
    ) -> PluginInstallState:
        """Install a plugin asynchronously.

        Args:
            plugin: ProjectPlugin to install.
            reason: Install reason.

        Returns:
            PluginInstallState state instance.
        """
        env = self.plugin_installation_env(plugin)

        if (
            (
                reason == PluginInstallReason.AUTO
                and not self._requires_install(plugin, env=env)
            )
            or not plugin.is_installable()
            or self._is_mapping(plugin)
        ):
            state = PluginInstallState(
                plugin=plugin,
                reason=reason,
                status=PluginInstallStatus.SKIPPED,
                message=f"Plugin '{plugin.name}' does not require installation",
            )
            self.status_cb(state)
            return state

        self.status_cb(
            PluginInstallState(
                plugin=plugin,
                reason=reason,
                status=PluginInstallStatus.RUNNING,
            ),
        )

        try:
            async with plugin.trigger_hooks("install", self, plugin, reason):
                installer: PluginInstaller = getattr(
                    plugin,
                    "installer",
                    install_pip_plugin,
                )
                await installer(
                    project=self.project,
                    plugin=plugin,
                    reason=reason,
                    clean=self.clean,
                    force=self.force,
                    env=env,
                )
                state = PluginInstallState(
                    plugin=plugin,
                    reason=reason,
                    status=PluginInstallStatus.SUCCESS,
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
                    f"{plugin.type.descriptor.capitalize()} '{plugin.name}' "
                    f"could not be installed: {err}"
                ),
                details=await err.stderr,
            )
            self.status_cb(state)
            return state

    def _requires_install(
        self,
        plugin: ProjectPlugin,
        *,
        env: t.Mapping[str, str] | None = None,
    ) -> bool:
        try:
            pip_install_args = get_pip_install_args(
                self.project,
                plugin,
                env,
                if_missing=EnvVarMissingBehavior.raise_exception,
            )
        except EnvironmentVariableNotSetError as e:
            logger.warning(
                (
                    "Environment variable '%s' not set for '%s' `pip_url`, will not"
                    " attempt install"
                ),
                e.env_var,
                plugin.name,
            )
            return False

        venv = VirtualEnv(self.project.plugin_dir(plugin, "venv", make_dirs=False))
        return fingerprint(pip_install_args) != venv.read_fingerprint()

    @staticmethod
    def _is_mapping(plugin: ProjectPlugin) -> bool:
        """Check if a plugin is a mapping, as mappings are not installed.

        Mappings are `PluginType.MAPPERS` with extra attribute of `_mapping`
        which will indicate that this instance of the plugin is actually a
        mapping - and should not be installed.

        Args:
            plugin: ProjectPlugin to evaluate.

        Returns:
            A boolean determining if the given plugin is a mapping (of type
            `PluginType.MAPPERS`).
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
        plugin_settings_service = PluginSettingsService(self.project, plugin)
        with self.project.settings.feature_flag(
            FeatureFlags.STRICT_ENV_VAR_MODE,
            raise_error=False,
        ) as strict_env_var_mode:
            expanded_project_env = expand_env_vars(
                self.project.settings.env,
                os.environ,
                if_missing=EnvVarMissingBehavior(strict_env_var_mode),
            )
            return {
                "MELTANO__PYTHON_VERSION": (
                    f"{sys.version_info.major}.{sys.version_info.minor}"
                ),
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


class PluginInstaller(t.Protocol):
    """Prototype function for plugin installation.

    All plugin installation functions must support at least the specified
    parameters, and also accept additional unused keyword arguments.
    """

    async def __call__(
        self,
        *,
        project: Project,
        plugin: ProjectPlugin,
        **kwargs,  # noqa: ANN003
    ) -> None:
        """Install the plugin.

        Args:
            project: Meltano Project.
            plugin: `ProjectPlugin` to install.
            kwargs: Additional arguments for the installation of the plugin.
        """


def get_pip_install_args(
    project: Project,
    plugin: ProjectPlugin,
    env: t.Mapping[str, str] | None = None,
    if_missing: EnvVarMissingBehavior | None = None,
) -> list[str]:
    """Get the pip install arguments for the given plugin.

    Args:
        project: Meltano Project.
        plugin: `ProjectPlugin` to get pip install arguments for.
        env: Optional environment variables to use when expanding the pip install args.
        if_missing: The behaviour flow to follow when a environment variable is not
            present when expanding the pip URL

    Returns:
        The list of pip install arguments for the given plugin.
    """
    with project.settings.feature_flag(
        FeatureFlags.STRICT_ENV_VAR_MODE,
        raise_error=False,
    ) as strict_env_var_mode:
        return shlex.split(
            expand_env_vars(
                plugin.pip_url,
                env,
                if_missing=if_missing or EnvVarMissingBehavior(strict_env_var_mode),
            )
            or "",
        )


async def install_pip_plugin(
    *,
    project: Project,
    plugin: ProjectPlugin,
    clean: bool = False,
    force: bool = False,
    env: t.Mapping[str, str] | None = None,
    **kwargs,  # noqa: ANN003, ARG001
) -> None:
    """Install the plugin with pip.

    Args:
        project: Meltano Project.
        plugin: `ProjectPlugin` to install.
        clean: Flag to clean install.
        force: Whether to ignore the Python version required by plugins.
        env: Environment variables to use when expanding the pip install args.
        kwargs: Unused additional arguments for the installation of the plugin.

    Raises:
        ValueError: If the venv backend is not supported.
    """
    pip_install_args = get_pip_install_args(project, plugin, env=env)
    backend = project.settings.get("venv.backend")

    if backend == "virtualenv":
        service = VenvService(
            project=project,
            python=plugin.python,
            namespace=plugin.type,
            name=plugin.venv_name,
        )
    elif backend == "uv":  # pragma: no cover
        service = UvVenvService(
            project=project,
            python=plugin.python,
            namespace=plugin.type,
            name=plugin.venv_name,
        )
    else:  # pragma: no cover
        msg = f"Unsupported venv backend: {backend}"
        raise ValueError(msg)

    await service.install(
        pip_install_args=("--ignore-requires-python", *pip_install_args)
        if force
        else pip_install_args,
        clean=clean,
        env={
            **os.environ,
            **project.dotenv_env,
            **project.meltano.env,
        },
    )
