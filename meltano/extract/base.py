import pandas as pd
import asyncio

from typing import Sequence
from abc import ABC, abstractmethod
from meltano.stream.writer import MeltanoStreamWriter
from meltano.common.entity import MeltanoEntity


class MeltanoExtractor:
    def __init__(self, writer: MeltanoStreamWriter, service: 'MeltanoService'):
        self.service = service
        self.writer = writer

    @abstractmethod
    async def entities(self):
        """
        Generates a list of MeltanoEntity from the data source.
        """
        pass

    @abstractmethod
    async def extract(self, entity: MeltanoEntity):
        """
        Generate DataFrame for a specified entity.
        """
        pass

    def run(self):
        loop = asyncio.get_event_loop()
        self.writer.send_all(loop, self)
