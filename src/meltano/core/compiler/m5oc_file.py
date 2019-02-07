import json
from typing import Dict
from pathlib import Path


class M5ocFile:
    def __init__(self, path: Path, content: Dict):
        self.path = path
        self.content = content

    @classmethod
    def load(cls, file):
        return cls(file.name, json.load(file))
