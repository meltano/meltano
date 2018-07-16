import asyncio
import pyarrow as pa
import pandas as pd
import json

from meltano.common.service import MeltanoService
from meltano.extract.base import MeltanoExtractor


def sample_data(i, columns):
  d = {
    column: range(50000) for column in columns
  }

  # gather the source data in the DataFrame
  df = pd.DataFrame(data=d)

  # should be constructed from a elt.schema.Schema
  schema = pa.schema([
    pa.field(column, pa.int32()) for column in columns
  ])

  # convert it to a pyarrow.Table
  table = pa.Table.from_pandas(df, schema=schema, preserve_index=False)

  # very important, we need to know the source_table
  table = table.replace_schema_metadata(metadata={
    'meltano': json.dumps({
      'entity_name': "com.meltano.marketo:Project",
      'jobid': "8857"
    })
  })

  return table


class SampleExtractor(MeltanoExtractor):
    async def extract_all(self):
        i = 0
        while True:
            i = i + 1
            await asyncio.sleep(10)
            yield sample_data(i, ['a', 'b', 'c'])


MeltanoService.register_extractor("com.meltano.extract.sample", SampleExtractor)
