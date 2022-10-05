"""Meltano UI worker thread definition."""

from __future__ import annotations

import logging
import threading
import time
import traceback

import click
import requests

from meltano.core.project_settings_service import ProjectSettingsService

logger = logging.getLogger(__name__)

SUCCESS_STATUS_CODE = 200


class UIAvailableWorker(threading.Thread):
    """A thread subclass for Meltano UI workers."""

    def __init__(self, project):
        """Initialize the `UIAvailableWorker` thread.

        Args:
            project: The Meltano project.
        """
        super().__init__()
        self.project = project
        self.settings_service = ProjectSettingsService(self.project)
        self._terminate = False

    def run(self) -> None:
        """Run the thread, and report when the Meltano UI becomes available."""
        url = f"http://localhost:{self.settings_service.get('ui.bind_port')}"
        headers = {"Host": self.settings_service.get("ui.server_name")}

        while not self._terminate:
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == SUCCESS_STATUS_CODE:
                    click.secho(f"Meltano UI is now available at {url}", fg="green")
                    self._terminate = True
            except Exception:
                logger.debug(
                    f"Exception encountered while trying to run Meltano UI:\n{traceback.format_exc()}"
                )

            time.sleep(2)

    def stop(self):
        """Stop the thread."""
        self._terminate = True
