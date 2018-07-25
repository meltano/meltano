import asyncio
import pyarrow as pa
import pandas as pd
import json
import logging

from itertools import count
from meltano.common.service import MeltanoService
from meltano.common.entity import Entity
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
        yield Entity('Sample')


    async def extract(self, entity):
        for i in count():
            await asyncio.sleep(1)
            yield sample_data(i, ['a', 'b', 'c'])


MeltanoService.register_extractor("com.meltano.extract.sample", SampleExtractor)
