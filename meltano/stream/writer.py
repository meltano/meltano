import pyarrow as pa
import json


class MeltanoStreamWriter:
    def __init__(self, stream, chunksize=1000):
        self.chunksize = chunksize
        self.stream = stream

    def send(self, sink, data):
        writer = pa.RecordBatchStreamWriter(sink, data.schema)
        writer.write_table(data, chunksize=self.chunksize)
        writer.close()

    async def write(self, sink, extractor):
        async for entity in extractor.entities():
            async for frame in extractor.extract(entity):
                self.send(sink, self.encode(entity, frame))

    def encode(self, entity, frame, **metadata):
        page = pa.Table.from_pandas(frame, preserve_index=False)
        page = page.replace_schema_metadata(metadata={
            'meltano': json.dumps({
                'entity': entity,
                'metadata': metadata
            })
        })

        return page

    def send_all(self, loop, extractor: 'MeltanoExtractor'):
        with open(self.stream.fd, 'wb') as sink:
            loop.run_until_complete(
                self.write(sink, extractor)
            )
