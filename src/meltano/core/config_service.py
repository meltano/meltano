"""Service to manage meltano.yml."""
from __future__ import annotations

import logging
import os
from contextlib import contextmanager

import yaml

from meltano.core import bundle
from meltano.core.project import Project
from meltano.core.setting_definition import SettingDefinition

logger = logging.getLogger(__name__)


class ConfigService:
    """Service to manage meltano.yml."""

    def __init__(self, project: Project, use_cache=True):
        """Create a new project configuration service.

        Args:
            project: the project to configure.
            use_cache: whether to use the cache or not.
        """
        self.project = project

        self._settings = None
        self._current_meltano_yml = None
        self._use_cache = use_cache

    @property
    def settings(self):
        """Return the project settings.

        Returns:
            The project settings.
        """
        if self._settings is None:
            with open(bundle.root / "settings.yml") as settings_yaml:
                settings = yaml.safe_load(settings_yaml)
            self._settings = list(map(SettingDefinition.parse, settings["settings"]))

        return self._settings

    @property
    def current_meltano_yml(self):
        """Return the current meltano.yml contents.

        Returns:
            The contents of meltano.yml.
        """
        if self._current_meltano_yml is None or not self._use_cache:
            self.project.clear_cache()
            self._current_meltano_yml = self.project.meltano
        return self._current_meltano_yml

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

        self._current_meltano_yml = None

    @contextmanager
    def update_active_environment(self):
        """Update active environment.

        Yields:
            active environment
        """
        environment = self.project.active_environment

        with self.update_meltano_yml() as meltano_yml:
            environments = meltano_yml.environments

            # find the proper environment to update
            env_idx, _ = next(
                (idx, env) for idx, env in enumerate(environments) if env == environment
            )

            active_environment = environments[env_idx]
            yield active_environment

        self.project.active_environment = active_environment

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
