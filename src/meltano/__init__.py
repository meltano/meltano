import os
from pathlib import Path


__version__ = Path(os.path.dirname(__file__), "../../VERSION").open("r").read().strip()
