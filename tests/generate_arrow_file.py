import pyarrow as pa
import pandas as pd
import json
import sys
import os


d = {
  'id': range(200),
  'name': ["John", "Steve"] * 100,
  'age': [43, 33] * 100
}

# gather the source data in the DataFrame
df = pd.DataFrame(data=d)

# should be constructed from a elt.schema.Schema
schema = pa.schema([
  pa.field('name', pa.string()),
  pa.field('age', pa.int32()),
])

# convert it to a pyarrow.Table
table = pa.Table.from_pandas(df, schema=schema, preserve_index=False)

# very important, we need to know the source_table
table = table.replace_schema_metadata(metadata={
  'meltano': json.dumps({
    'entity_name': "project",
    'jobid': "8857"
  })
})

# write to stdout
#sink = os.fdopen(sys.stdout.fileno(), "wb")
sink = open("test.arrow", "wb")
#sink = pa.BufferOutputStream()
writer = pa.RecordBatchStreamWriter(sink, table.schema)

# manage chunking
chunk_size = 5
for batch in table.to_batches():
  writer.write_batch(batch)

writer.close()
sink.close()
