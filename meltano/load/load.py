from abc import ABC, abstractmethod
from meltano import MeltanoService, MeltanoEntity
from meltano.stream import MeltanoStream


class MeltanoLoader(ABC):
    def __init__(self, stream: MeltanoStream, service: MeltanoService):
        self.service = service
        self.stream = stream

    def start_load(self):
        pass

    @abstractmethod
    def load(self, entity: MeltanoEntity, data):
        pass

    def end_load(self):
        pass

    def receive(self):
        reader = self.stream.create_reader(self)
        self.start_load()
        reader.read()
        self.end_load()
