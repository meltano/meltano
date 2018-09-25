from abc import ABC, abstractmethod


class MeltanoExtractor(ABC):
    @abstractmethod
    def extract(self):
        pass
