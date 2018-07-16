import asyncio

from abc import ABC, abstractmethod
from meltano.common.service import MeltanoService
from meltano.common.entity import MeltanoEntity
from meltano.stream.reader import MeltanoStreamReader


class MeltanoLoader(ABC):
    def __init__(self, reader: MeltanoStreamReader, service: MeltanoService):
        self.service = service
        self.reader = reader

    def start_load(self):
        pass

    @abstractmethod
    def load(self, entity: MeltanoEntity, data):
        pass

    def end_load(self):
        pass

    def run(self):
        loop = asyncio.get_event_loop()
        self.start_load()
        self.reader.read_all(loop, self)
        self.end_load()
