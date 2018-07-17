import asyncio
import pyarrow as pa
import pandas as pd
import json
import logging

from meltano.common.service import MeltanoService
from meltano.extract.base import MeltanoExtractor


def sample_data(i, columns):
  d = {
    column: range(50000) for column in columns
  }

  # gather the source data in the DataFrame
  df = pd.DataFrame(data=d)
  return df


class SampleExtractor(MeltanoExtractor):
    async def entities(self):
        yield ['a', 'b', 'c']

    async def extract(self, entity):
        # logging.debug(f"Extracting data for {entity}")
        for i in range(1000):
            await asyncio.sleep(3)
            yield sample_data(i, entity)


MeltanoService.register_extractor("com.meltano.extract.sample", SampleExtractor)
