"""SingerTarget and supporting classes.

This module contains the SingerTarget class as well as a supporting BookmarkWriter class.
"""
import json
import logging
from datetime import datetime
from typing import List

from meltano.core.behavior.hookable import hook
from meltano.core.db import project_engine
from meltano.core.job import Job, Payload
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.setting_definition import SettingDefinition

from . import PluginType, SingerPlugin

logger = logging.getLogger(__name__)


class BookmarkWriter:
    """A basic bookmark writer suitable for use as an output handler."""

    def __init__(self, job: Job, session: object, payload_flag: int = Payload.STATE):
        """Bookmark writer with a writelines implementation to support ingesting and persisting state messages.

        Args:
            job: meltano elt job associated with this invocation and who's state will be updated.
            session: SQLAlchemy session/engine object to be used to update state.
            payload_flag: a valid payload flag, one of Payload.STATE or Payload.INCOMPLETE_STATE.
        """
        self.job = job
        self.session = session
        self.payload_flag = payload_flag

    def writeline(self, line: str):
        """Persist a state entry.

        Args:
            line: raw json state line to decode/store
        """
        if self.job is None:
            logging.info(
                "Running outside a Job context: incremental state could not be updated."
            )
            return

        new_state = {}
        try:
            new_state = json.loads(line)
        except Exception:
            logging.warning(
                "Received state is invalid, incremental state has not been updated"
            )

        job = self.job
        job.payload["singer_state"] = new_state
        job.payload_flags |= self.payload_flag
        try:
            job.save(self.session)
        except Exception:
            logging.warning(
                "Unable to persist state, or received state is invalid, incremental state has not been updated"
            )
        else:
            logging.info(f"Incremental state has been updated at {datetime.utcnow()}.")
            logging.debug(f"Incremental state: {new_state}")


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
        return {"config": f"target.{self.instance_uuid}.config.json"}

    @property
    def output_files(self):
        return {"state": "new_state.json"}

    @hook("before_invoke")
    async def setup_bookmark_writer_hook(
        self, plugin_invoker: PluginInvoker, exec_args: List[str]
    ):
        """Before invoke hook to trigger setting up the bookmark writer for this target.

        Args:
            plugin_invoker: The invocation handler of the plugin instance.
            exec_args: List of subcommand/args that we where invoked with.
        """
        if exec_args is None:
            exec_args = []

        if "--discover" in exec_args or "--help" in exec_args:
            return

        self.setup_bookmark_writer(plugin_invoker)

    def setup_bookmark_writer(self, plugin_invoker: PluginInvoker):
        """Configure the bookmark writer as an additional output handler on the invoker if running in a pipeline context.

        This leverages calling back to PluginInvokers.add_output_handler to attach an additional
        output handler (the BookmarkWriter) to handle persisting state messages.

        Args:
            plugin_invoker: The invocation handler who's add_out_handler method will be called to attach the bookmark writer
            as an additional output handler.
        """
        elt_context = plugin_invoker.context
        if not elt_context or not elt_context.job or not elt_context.session:
            return

        incomplete_state = elt_context.full_refresh and elt_context.select_filter
        payload_flag = Payload.INCOMPLETE_STATE if incomplete_state else Payload.STATE

        plugin_invoker.add_output_handler(
            plugin_invoker.StdioSource.STDOUT,
            BookmarkWriter(elt_context.job, elt_context.session, payload_flag),
        )
