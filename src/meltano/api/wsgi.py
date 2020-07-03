import os
import logging
import warnings
import meltano
import importlib

from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService

_project = Project.find()
_settings_service = ProjectSettingsService(_project)

_bind_host = _settings_service.get("ui.bind_host")
_bind_port = _settings_service.get("ui.bind_port")
bind = f"{_bind_host}:{_bind_port}"

workers = _settings_service.get("ui.workers")
forwarded_allow_ips = _settings_service.get("ui.forwarded_allow_ips")

timeout = 600


def on_reload(arbiter):
    importlib.reload(meltano)
    logging.info(f"Meltano version reloaded to {meltano.__version__}")
