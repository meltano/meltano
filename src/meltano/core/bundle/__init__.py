"""
This module files should be created via
`make bundle` at the project root.
"""

import os
from pathlib import Path


def root() -> Path:
    return Path(os.path.dirname(__file__))


def find(file_path: Path) -> Path:
    return root().joinpath(file_path)
