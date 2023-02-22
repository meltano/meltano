"""Service to manage meltano.yml."""

from __future__ import annotations

import logging
import os
import sys
import typing as t
from contextlib import contextmanager

import yaml

from meltano.core import bundle
from meltano.core.meltano_file import MeltanoFile
from meltano.core.setting_definition import SettingDefinition

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from cached_property import cached_property

if t.TYPE_CHECKING:
    from meltano.core.project import Project

logger = logging.getLogger(__name__)


class ConfigService:
    """Service to manage meltano.yml."""

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
        with open(str(bundle.root / "settings.yml")) as settings_yaml:
            settings_yaml_content = yaml.safe_load(settings_yaml)
        return [SettingDefinition.parse(x) for x in settings_yaml_content["settings"]]

    @cached_property
    def current_meltano_yml(self) -> MeltanoFile:
        """Return the current `meltano.yml` contents.

        Returns:
            The contents of `meltano.yml`.
        """
        return self.project.meltano

    @contextmanager
    def update_meltano_yml(self):
        """Update meltano.yml.

        This method is a context manager that will update meltano.yml with the
        contents of the context.

        Yields:
            The contents of meltano.yml.
        """
        with self.project.meltano_update() as meltano_yml:
            yield meltano_yml

    @contextmanager
    def update_active_environment(self):
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
    def current_config(self):
        """Return the current configuration.

        Returns:
            The current configuration.
        """
        return self.current_meltano_yml.extras

    def update_config(self, config):
        """Update top-level Meltano configuration.

        Args:
            config: configuration dict
        """
        with self.update_meltano_yml() as meltano_yml:
            meltano_yml.extras = config

    def make_meltano_secret_dir(self):
        """Create the secret directory."""
        os.makedirs(self.project.meltano_dir(), exist_ok=True)

    @property
    def env(self):
        """Return the top-level env vars from meltano.yml.

        Returns:
            A dictionary of (unexpanded) environment variables.
        """
        return self.current_meltano_yml.env
