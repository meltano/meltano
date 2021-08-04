import json
import logging
from datetime import datetime
from typing import Dict

from meltano.core.behavior.hookable import hook
from meltano.core.db import project_engine
from meltano.core.job import Payload
from meltano.core.setting_definition import SettingDefinition

from . import PluginType, SingerPlugin

logger = logging.getLogger(__name__)


class BookmarkWriter:
    def __init__(self, job, session, payload_flag=Payload.STATE):
        self.job = job
        self.session = session
        self.payload_flag = payload_flag

    def writeline(self, line):
        if self.job is None:
            logging.info(
                "Running outside a Job context: incremental state could not be updated."
            )
            return

        try:
            new_state = json.loads(line)
            job = self.job

            job.payload["singer_state"] = new_state
            job.payload_flags |= self.payload_flag
            job.save(self.session)

            logging.info(f"Incremental state has been updated at {datetime.utcnow()}.")
            logging.debug(f"Incremental state: {new_state}")
        except Exception:
            logging.warning(
                "Received state is invalid, incremental state has not been updated"
            )


class SingerTarget(SingerPlugin):
    __plugin_type__ = PluginType.LOADERS

    EXTRA_SETTINGS = [
        SettingDefinition(name="_dialect", value="$MELTANO_LOADER_NAMESPACE"),
        SettingDefinition(name="_target_schema", value="$MELTANO_LOAD_SCHEMA"),
    ]

    def exec_args(self, plugin_invoker):
        args = ["--config", plugin_invoker.files["config"]]

        return args

    @property
    def config_files(self):
        return {"config": "target.config.json"}

    @property
    def output_files(self):
        return {"state": "new_state.json"}

    @hook("before_invoke")
    def setup_bookmark_writer_hook(self, plugin_invoker, exec_args=[]):
        if "--discover" in exec_args or "--help" in exec_args:
            return
        self.setup_bookmark_writer(plugin_invoker, exec_args)

    def setup_bookmark_writer(self, plugin_invoker, exec_args=[]):
        elt_context = plugin_invoker.context
        incomplete_state = elt_context.full_refresh and elt_context.select_filter
        payload_flag = Payload.INCOMPLETE_STATE if incomplete_state else Payload.STATE
        plugin_invoker.add_output_handler(
            plugin_invoker.STD_OUT,
            BookmarkWriter(elt_context.job, elt_context.session, payload_flag),
        )
