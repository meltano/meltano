import logging
import requests
import threading
import time
import webbrowser
import click

from meltano.core.project_settings_service import ProjectSettingsService


class UIAvailableWorker(threading.Thread):
    def __init__(self, project, open_browser=False):
        super().__init__()

        self.project = project
        self.open_browser = open_browser

        self.settings_service = ProjectSettingsService(self.project)

        self._terminate = False

    def run(self):
        bind_port = self.settings_service.get("ui.bind_port")
        url = f"http://localhost:{bind_port}"

        server_name = self.settings_service.get("ui.server_name")
        headers = {"Host": server_name}

        while not self._terminate:
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    click.secho(f"Meltano UI is now available at {url}", fg="green")
                    if self.open_browser:
                        webbrowser.open(url)
                    self._terminate = True
            except:
                pass

            time.sleep(2)

    def stop(self):
        self._terminate = True
