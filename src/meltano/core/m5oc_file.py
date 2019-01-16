import json

from typing import Dict
from pathlib import Path


class DesignMissingError(Exception):
    pass


class ConnectionNotFoundError(Exception):
    pass


class M5ocFile:
    def __init__(self, content: Dict):
        self.content = content

    @classmethod
    def load(cls, file):
        return M5ocFile(json.load(file))

    @property
    def designs(self):
        return self.content["designs"]

    def design(self, design_name: str) -> Dict:
        try:
            return next(e for e in self.designs if e["name"] == design_name)
        except StopIteration:
            raise DesignMissingError(f"{design_name} not found.")

    def connection(self, connection_name: str) -> Dict:
        try:
            return self.content["connection"]
        except StopIteration:
            raise ConnectionNotFoundError(f"{connection_name} not found.")
