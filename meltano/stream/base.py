from meltano.schema import Schema
from meltano.common.service import MeltanoService

from .writer import MeltanoStreamWriter
from .reader import MeltanoStreamReader


class MeltanoStream:
    def __init__(self, fd):
        """
        fd: file descriptor to use, it should be non-blocking.
        """
        self.fd = fd

    def create_reader(self):
        return MeltanoStreamReader(self)

    def create_writer(self):
        """
        Send a DataFrame to the stream.
        """
        return MeltanoStreamWriter(self)
