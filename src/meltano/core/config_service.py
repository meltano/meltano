"""Service to manage meltano.yml."""

from __future__ import annotations

import typing as t
from contextlib import contextmanager
from functools import cached_property

import structlog
import yaml

from meltano.core import bundle
from meltano.core.behavior.addon import MeltanoAddon
from meltano.core.setting_definition import SettingDefinition

if t.TYPE_CHECKING:
    from collections.abc import Generator

    from meltano.core.meltano_file import MeltanoFile
    from meltano.core.project import Project

logger = structlog.stdlib.get_logger(__name__)


class ConfigService:
    """Service to manage meltano.yml."""

    addon: MeltanoAddon[SettingDefinition] = MeltanoAddon("meltano.settings")

    def __init__(self, project: Project):
        """Create a new project configuration service.

        Args:
            project: the project to configure.
        """
        self.project = project

    @cached_property
    def settings(self) -> list[SettingDefinition]:
        """Return the project settings.

        Returns:
            The project settings.
        """
        with bundle.root.joinpath("settings.yml").open() as settings_yaml:
            content = yaml.safe_load(settings_yaml)

        builtin = [SettingDefinition.parse(x) for x in content["settings"]]
        addons = list(self.addon.get_all())
        return builtin + addons

    @cached_property
    def current_meltano_yml(self) -> MeltanoFile:
        """Return the current `meltano.yml` contents.

        Returns:
            The contents of `meltano.yml`.
        """
        return self.project.meltano

    @contextmanager
    def update_meltano_yml(self) -> Generator[MeltanoFile, None, None]:
        """Update meltano.yml.

        This method is a context manager that will update meltano.yml with the
        contents of the context.

        Yields:
            The contents of meltano.yml.
        """
        with self.project.meltano_update() as meltano_yml:
            yield meltano_yml

    @contextmanager
    def update_active_environment(self):  # noqa: ANN201
        """Update active environment.

        Yields:
            active environment
        """
        environment = self.project.environment
        with self.update_meltano_yml() as meltano_yml:
            environments = meltano_yml.environments
            # find the proper environment to update
            env_idx, _ = next(
                (idx, env) for idx, env in enumerate(environments) if env == environment
            )
            yield environments[env_idx]

    @property
    def current_config(self):  # noqa: ANN201
        """Return the current configuration.

        Returns:
            The current configuration.
        """
        return self.current_meltano_yml.extras

    def update_config(self, config: dict[str, t.Any]) -> None:
        """Update top-level Meltano configuration.

        Args:
            config: configuration dict
        """
        with self.update_meltano_yml() as meltano_yml:
            meltano_yml.extras = config

    @property
    def env(self) -> dict[str, str | None]:
        """Return the top-level env vars from meltano.yml.

        Returns:
            A dictionary of (unexpanded) environment variables.
        """
        return self.current_meltano_yml.env
