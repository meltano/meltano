import json

from typing import Dict
from pathlib import Path
from .design_helper import DesignHelper
from meltano.core.compiler.m5oc_file import M5ocFile

class DesignMissingError(Exception):
    pass


class ConnectionNotFoundError(Exception):
    pass


class M5ocCollectionFile(M5ocFile):
    @property
    def designs(self):
        return list(map(DesignHelper, self.content["designs"]))

    @property
    def reports(self):
        return self.content["reports"]

    def connection(self, connection_name: str) -> Dict:
        try:
            return self.content["connection"]
        except StopIteration:
            raise ConnectionNotFoundError(f"{connection_name} not found.")

    def design(self, design_name: str) -> Dict:
        try:
            return next(e for e in self.designs if e["name"] == design_name)
        except StopIteration:
            raise DesignMissingError(f"{design_name} not found.")

    def report(self, report_name: str) -> Dict:
        try:
            return next(e for e in self.reports if e["name"] == report_name)
        except StopIteration:
            raise DesignMissingError(f"{report_name} not found.")
