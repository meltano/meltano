import os
import logging
import warnings
import meltano
import importlib
from gunicorn.glogging import CONFIG_DEFAULTS

from meltano.core.logging.utils import FORMAT
from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService

_project = Project.find()
_settings_service = ProjectSettingsService(_project)

logconfig_dict = CONFIG_DEFAULTS.copy()
logconfig_dict["loggers"].pop("gunicorn.access")
logconfig_dict["loggers"]["gunicorn.error"]["propagate"] = False
logconfig_dict["formatters"]["generic"] = {"format": FORMAT}

loglevel = _settings_service.get("cli.log_level")

_bind_host = _settings_service.get("ui.bind_host")
_bind_port = _settings_service.get("ui.bind_port")
bind = f"{_bind_host}:{_bind_port}"

workers = _settings_service.get("ui.workers")
forwarded_allow_ips = _settings_service.get("ui.forwarded_allow_ips")

timeout = 600


def on_reload(arbiter):
    importlib.reload(meltano)
    logging.info(f"Meltano version reloaded to {meltano.__version__}")
