import json
from pathlib import Path
from typing import Dict


class M5ocFile:
    def __init__(self, path: Path, content: Dict):
        self.path = path
        self.content = content

    @classmethod
    def load(cls, file):
        return cls(file.name, json.load(file))
