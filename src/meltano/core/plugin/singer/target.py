"""SingerTarget and supporting classes."""

from __future__ import annotations

import json
import typing as t
from datetime import datetime, timezone

from structlog.stdlib import get_logger

from meltano.core.behavior.hookable import hook
from meltano.core.job import Payload
from meltano.core.setting_definition import SettingDefinition
from meltano.core.state_service import SINGER_STATE_KEY, StateService

from . import PluginType, SingerPlugin

if t.TYPE_CHECKING:
    from pathlib import Path

    from sqlalchemy.orm import Session

    from meltano.core.job import Job
    from meltano.core.plugin_invoker import PluginInvoker

logger = get_logger(__name__)


class BookmarkWriter:
    """A basic bookmark writer suitable for use as an output handler.

    Has a writelines method to support ingesting and persisting state messages.
    """

    def __init__(
        self,
        job: Job | None,
        session: Session,
        payload_flag: Payload = Payload.STATE,
        state_service: StateService | None = None,
    ):
        """Initialize the `BookmarkWriter`.

        Args:
            job: meltano el or meltano elt job associated with this invocation and whose
                state will be updated.
            session: SQLAlchemy session/engine object to be used to update state.
            payload_flag: A payload flag.
            state_service: `StateService` to use for bookmarking state.
        """
        self.job = job
        self.session = session
        self.state_service = state_service or StateService(session=self.session)
        self.payload_flag = payload_flag

    def writeline(self, line: str) -> None:
        """Persist a state entry.

        Args:
            line: raw json state line to decode/store
        """
        if self.job is None:
            logger.info(
                "Running outside a Job context: "
                "incremental state could not be updated.",
            )
            return

        new_state = {}
        try:
            new_state = json.loads(line)
        except Exception:  # noqa: BLE001
            logger.warning(
                "Received state is invalid, incremental state has not been updated",
            )
            return

        job = self.job
        job.payload[SINGER_STATE_KEY] = new_state
        job.payload_flags = Payload(max(self.payload_flag, job.payload_flags))

        try:
            job.save(self.session)
        except Exception as e:  # pragma: no cover  # noqa: BLE001
            logger.warning("Failed to persist job to the system database: %s", e)

        try:
            self.state_service.add_state(
                job,
                json.dumps(job.payload),
                job.payload_flags,
            )
        except Exception:  # pragma: no cover  # noqa: BLE001
            logger.warning(
                "Unable to persist state, or received state is invalid, "
                "incremental state has not been updated",
                exc_info=True,
            )
        else:
            logger.info(
                f"Incremental state has been updated at {datetime.now(tz=timezone.utc)}.",  # noqa: E501, G004
            )
            logger.debug(f"Incremental state: {new_state}")  # noqa: G004


class SingerTarget(SingerPlugin):
    """A plugin for singer targets."""

    __plugin_type__ = PluginType.LOADERS

    EXTRA_SETTINGS: t.ClassVar[list[SettingDefinition]] = [
        *SingerPlugin.EXTRA_SETTINGS,
        SettingDefinition(name="_dialect", value="$MELTANO_LOADER_NAMESPACE"),
    ]

    def exec_args(self, plugin_invoker: PluginInvoker) -> list[str | Path]:
        """Get command-line args to pass to the plugin.

        Args:
            plugin_invoker: PluginInvoker running this target.

        Returns:
            Command-line args for target
        """
        return ["--config", plugin_invoker.files["config"]]

    @property
    def config_files(self) -> dict[str, str]:
        """Get config files for this target.

        Returns:
            The config_files for this target.
        """
        return {
            "config": f"target.{self.instance_uuid}.config.json",
            "singer_sdk_logging": "target.singer_sdk_logging.json",
            "pipelinewise_singer_logging": "target.pipelinewise_logging.conf",
        }

    @property
    def output_files(self) -> dict[str, str]:
        """Get output files for this target.

        Returns:
            The output files for this target.
        """
        return {"state": "new_state.json"}

    @hook("before_invoke")
    async def setup_bookmark_writer_hook(
        self,
        plugin_invoker: PluginInvoker,
        exec_args: list[str] | None,
    ) -> None:
        """Before invoke hook to trigger setting up the bookmark writer for this target.

        Args:
            plugin_invoker: The invocation handler of the plugin instance.
            exec_args: List of subcommand/args that we where invoked with.
        """
        exec_args = exec_args or []

        if "--discover" in exec_args or "--help" in exec_args:
            return

        self.setup_bookmark_writer(plugin_invoker)

    def setup_bookmark_writer(self, plugin_invoker: PluginInvoker) -> None:
        """Configure the bookmark writer.

        If running in a pipeline context, we configure the bookmark writer as
        an additional output handler on the invoker.

        This leverages calling back to `PluginInvokers.add_output_handler` to
        attach an additional output handler (the `BookmarkWriter`) to handle
        persisting state messages.

        Args:
            plugin_invoker: The invocation handler whose `add_out_handler` method
                will be called to attach the bookmark writer as an additional
                output handler.
        """
        elt_context = plugin_invoker.context
        if not elt_context or not elt_context.job or not elt_context.session:
            return

        payload_flag = (
            Payload.INCOMPLETE_STATE
            if elt_context.should_merge_states()
            else Payload.STATE
        )

        plugin_invoker.add_output_handler(
            plugin_invoker.StdioSource.STDOUT,
            BookmarkWriter(elt_context.job, elt_context.session, payload_flag),
        )
