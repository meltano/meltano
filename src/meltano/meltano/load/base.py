import asyncio
import pyarrow

from abc import ABC, abstractmethod
from meltano.common.service import MeltanoService
from meltano.common.entity import Entity
from meltano.stream.reader import MeltanoStreamReader


class MeltanoLoader(ABC):
    def __init__(self, reader: MeltanoStreamReader, service: MeltanoService):
        self.service = service
        self.reader = reader

    def start_load(self):
        pass

    @abstractmethod
    def load(self, source_name, entity: Entity, data):
        pass

    def integrate(self, metadata, batch):
        source, alias = metadata['entity_id'].split(':')[-2:] # two last part
        entity = self.service.get_entity(metadata['entity_id'])

        return self.load(source, entity, batch.to_pandas())

    def end_load(self):
        pass

    def run(self):
        loop = asyncio.get_event_loop()
        self.start_load()
        self.reader.read_all(loop, self)
        self.end_load()
