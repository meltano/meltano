import pyarrow as pa
import json
import asyncio


class MeltanoStreamWriter:
    def __init__(self, stream, extractor):
        self.stream = stream
        self.extractor = extractor

    def send(self, sink, data):
        writer = pa.RecordBatchStreamWriter(sink, data.schema)
        writer.write_table(data, chunksize=100)
        writer.close()

    async def write(self):
        with open(self.stream.fd, 'wb') as sink:
            async for frame in self.extractor.extract_all():
                self.send(sink, self.encode(frame))

    def encode(self, frame):
        page = pa.Table.from_pandas(frame, preserve_index=False)
        page = page.replace_schema_metadata(metadata={
            'meltano': json.dumps({
                'entity_name': "com.meltano.marketo:Project",
                'jobid': "8857"
                })
            })

        return page

    def send_all(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.write())
