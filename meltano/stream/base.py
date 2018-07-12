from meltano.schema import Schema
from meltano.common.service import MeltanoService

from .writer import MeltanoStreamWriter
from .reader import MeltanoStreamReader


class MeltanoStream:
    """
    Reads data serialized using the `MeltanoSink` writer.
    """
    def __init__(self, fd, schema: Schema):
        """
        fd: file descriptor to use, it should be non-blocking.
        """
        self.fd = fd
        self.schema = schema

    def create_reader(self, loader: 'MeltanoLoader'):
        return MeltanoStreamReader(self, loader)

    def create_writer(self, extractor: 'MeltanoExtractor'):
        """
        Send a DataFrame to the stream.
        """
        raise NotImplementedError()
