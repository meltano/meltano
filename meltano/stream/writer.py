import pyarrow as pa
import json


class MeltanoStreamWriter:
    def __init__(self, stream, chunksize=1000):
        self.chunksize = chunksize
        self.stream = stream

    def write(self, entity, frame):
        data = self.encode(entity, frame)

        writer = pa.RecordBatchStreamWriter(self._sink, data.schema)
        writer.write_table(data, chunksize=self.chunksize)
        writer.close()

    def encode(self, entity, frame, **metadata):
        page = pa.Table.from_pandas(frame, preserve_index=False)
        page = page.replace_schema_metadata(metadata={
            'meltano': json.dumps({
                'entity': entity,
                'metadata': metadata
            })
        })

        return page

    def open(self):
        self._sink = open(self.stream.fd, 'wb')

    def close(self):
        self._sink.close()
