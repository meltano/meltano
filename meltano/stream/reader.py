import select
import asyncio
import logging
import json
import pyarrow as pa

from meltano.common.entity import MeltanoEntity


class MeltanoStreamReader:
    def __init__(self, stream, loader):
        self.stream = stream
        self.loader = loader

    def integrate(self, stream, loop):
        """
        Read a DataFrame from the stream.
        """
        try:
            while select.select([stream],[],[], 0.0)[0]:
                if len(stream.peek()) == 0:
                    # hit EOF
                    break

                reader = pa.open_stream(stream)
                metadata = self.read_metadata(reader)
                for batch in reader:
                    self.loader.load(metadata, batch.to_pandas())
        except Exception as e:
            logging.error("Stream cannot be read: {}".format(e))
        finally:
            loop.stop()

    def read(self):
        tap = open(self.stream.fd, 'rb')

        loop = asyncio.get_event_loop()
        loop.add_reader(tap, self.integrate, tap, loop)
        loop.run_forever()

    def read_metadata(self, reader) -> MeltanoEntity:
        raw_metadata = reader.schema.metadata[b'meltano']
        raw_metadata = json.loads(raw_metadata.decode("utf-8"))

        # return self.service.entities[raw_metadata['entity_name']]
        return MeltanoEntity(raw_metadata)
