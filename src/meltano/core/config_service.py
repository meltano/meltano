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
    import sys

    from meltano.core.meltano_file import MeltanoFile
    from meltano.core.project import Project

    if sys.version_info >= (3, 13):
        from collections.abc import Generator
    else:
        from typing_extensions import Generator


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
        """Project settings."""
        with bundle.root.joinpath("settings.yml").open() as settings_yaml:
            content = yaml.safe_load(settings_yaml)

        builtin = [SettingDefinition.parse(x) for x in content["settings"]]
        addons = list(self.addon.get_all())
        return builtin + addons

    @cached_property
    def current_meltano_yml(self) -> MeltanoFile:
        """Current `meltano.yml` contents."""
        return self.project.meltano

    @contextmanager
    def update_meltano_yml(self) -> Generator[MeltanoFile]:
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
        """Current configuration."""
        return self.current_meltano_yml.extras

    def update_config(self, config: dict[str, t.Any]) -> None:
        """Update top-level Meltano configuration.

        Args:
            config: configuration dict
        """
        with self.update_meltano_yml() as meltano_yml:
            meltano_yml.extras = config

    @property
    def env(self) -> dict[str, str]:
        """Top-level (unexpanded) env vars from meltano.yml."""
        return self.current_meltano_yml.env
