from __future__ import annotations

from abc import ABC, abstractmethod


class MeltanoExtractor(ABC):
    @abstractmethod
    def extract(self):
        pass
