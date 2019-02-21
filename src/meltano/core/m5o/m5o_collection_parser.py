from pyhocon import ConfigFactory
from pathlib import Path
from enum import Enum

import json


class M5oCollectionParserError(Exception):
    def __init__(self, message, file_name, *args):
        self.message = message
        self.file_name = file_name
        super(M5oCollectionParserError, self).__init__(
            self.message, self.file_name, *args
        )


class M5oCollectionParserTypes(Enum):
    Dashboard = "dashboard"
    Report = "report"


class M5oCollectionParser:
    def __init__(self, directory, file_type):
        self.directory = directory
        self.file_type = file_type
        self.pattern = f"*.{self.file_type.value}.m5o"
        self.files = []

    def contents(self):
        files = self.parse()
        self.compile(files)
        return self.files

    def compile(self, files):
        self.files = files
        compiled_file_path = Path(self.directory).joinpath(
            f"{self.file_type.value}s.m5oc"
        )
        compiled_file = open(compiled_file_path, "w")
        compiled_file.write(json.dumps(self.files))
        compiled_file.close()

    def parse(self):
        files = []
        for file in Path(self.directory).glob(self.pattern):
            file_name = file.parts[-1]
            m5o_file = Path(self.directory).joinpath(file_name)
            with m5o_file.open() as f:
                files.append(json.load(f))

        return files
