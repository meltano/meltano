from __future__ import annotations

import logging
import threading
import time
import traceback
import webbrowser

import click
import requests

from meltano.core.project_settings_service import ProjectSettingsService

logger = logging.getLogger(__name__)

SUCCESS_STATUS_CODE = 200


class UIAvailableWorker(threading.Thread):
    def __init__(self, project, open_browser=False):
        super().__init__()
        self.project = project
        self.open_browser = open_browser
        self.settings_service = ProjectSettingsService(self.project)
        self._terminate = False

    def run(self):
        url = f"http://localhost:{self.settings_service.get('ui.bind_port')}"
        headers = {"Host": self.settings_service.get("ui.server_name")}

        while not self._terminate:
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == SUCCESS_STATUS_CODE:
                    click.secho(f"Meltano UI is now available at {url}", fg="green")
                    if self.open_browser:
                        webbrowser.open(url)
                    self._terminate = True
            except Exception:
                logger.debug(
                    f"Exception encountered while trying to run Meltano UI:\n{traceback.format_exc()}"
                )

            time.sleep(2)

    def stop(self):
        self._terminate = True
