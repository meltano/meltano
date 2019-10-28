import logging
import requests
import threading
import time
import webbrowser
from colorama import Fore


class UIAvailableWorker(threading.Thread):
    def __init__(self, url, open_browser=False):
        super().__init__()
        self._terminate = False

        self.url = url
        self.open_browser = open_browser

    def run(self):
        while not self._terminate:
            try:
                response = requests.get(self.url)
                if response.status_code == 200:
                    print(f"{Fore.GREEN}Meltano is available at {self.url}{Fore.RESET}")
                    if self.open_browser:
                        webbrowser.open(self.url)
                    self._terminate = True

            except:
                pass

            time.sleep(2)

    def stop(self):
        self._terminate = True
