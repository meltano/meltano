import pandas as pd
import asyncio
import logging

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
        Generates DataFrames for a specified entity.
        """
        pass

    async def extract_entity(self, entity):
        async for frame in self.extract(entity):
            self.writer.write(entity, frame)

    async def extract_all(self, loop, entities):
        tasks = []
        try:
            self.writer.open()
            async for entity in entities():
                tasks.append(
                    loop.create_task(self.extract_entity(entity))
                )

            # TODO: add timeout
            result = await asyncio.gather(*tasks)
        finally:
            logging.info("Shutting down")
            self.writer.close()

    def run(self):
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                self.extract_all(loop, self.entities)
            )
        finally:
            loop.close()
