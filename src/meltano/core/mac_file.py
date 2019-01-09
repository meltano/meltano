import json

from typing import Dict
from pathlib import Path


class ExploreMissingError(Exception):
    pass


class ConnectionNotFoundError(Exception):
    pass


class MACFile:
    def __init__(self, content: Dict):
        self.content = content

    @classmethod
    def load(cls, file):
        return MACFile(json.load(file))

    @property
    def explores(self):
        return self.content["explores"]

    def explore(self, explore_name: str) -> Dict:
        try:
            return next(e for e in self.explores if e["name"] == explore_name)
        except StopIteration:
            raise ExploreMissingError(f"{explore_name} not found.")

    def connection(self, connection_name: str) -> Dict:
        try:
            return self.content["connection"]
        except StopIteration:
            raise ConnectionNotFoundError(f"{connection_name} not found.")
