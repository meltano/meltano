import logging
import os
from contextlib import contextmanager

import meltano.core.bundle as bundle
import yaml

from .project import Project
from .setting_definition import SettingDefinition

logger = logging.getLogger(__name__)


class ConfigService:
    def __init__(self, project: Project, use_cache=True):
        self.project = project

        self._settings = None
        self._current_meltano_yml = None
        self._use_cache = use_cache

    @property
    def settings(self):
        if self._settings is None:
            with bundle.find("settings.yml").open() as settings_yaml:
                settings = yaml.safe_load(settings_yaml)
            self._settings = list(map(SettingDefinition.parse, settings["settings"]))

        return self._settings

    @property
    def current_meltano_yml(self):
        if self._current_meltano_yml is None or not self._use_cache:
            self._current_meltano_yml = self.project.meltano
        return self._current_meltano_yml

    @contextmanager
    def update_meltano_yml(self):
        with self.project.meltano_update() as meltano_yml:
            yield meltano_yml

        self._current_meltano_yml = None

    @property
    def current_config(self):
        return self.current_meltano_yml.extras

    def update_config(self, config):
        with self.update_meltano_yml() as meltano_yml:
            meltano_yml.extras = config

    def make_meltano_secret_dir(self):
        os.makedirs(self.project.meltano_dir(), exist_ok=True)
