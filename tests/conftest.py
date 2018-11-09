import pytest
import logging


logging.basicConfig(level=logging.INFO)

pytest_plugins = ["fixtures.db", "fixtures.fs", "fixtures.core"]
