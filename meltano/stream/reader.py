import select
import logging
import json
import pyarrow as pa

from meltano.common.entity import Entity


class MeltanoStreamReader:
    def __init__(self, stream):
        self.stream = stream

    def integrate(self, stream, loader, loop):
        """
        Read a DataFrame from the stream.
        """
        try:
            while select.select([stream],[],[], 0.0)[0]:
                if len(stream.peek()) == 0:
                    # hit EOF
                    break

                reader = pa.open_stream(stream)
                for batch in reader:
                    metadata = self.read_metadata(reader)
                    loader.integrate(metadata, batch)
        except Exception as e:
            logging.error("Stream cannot be read: {}".format(e))
        finally:
            loop.stop()

    def read_all(self, loop, loader: 'MeltanoLoader'):
        with open(self.stream.fd, 'rb') as tap:
            loop.add_reader(tap, self.integrate, tap, loader, loop)
            loop.run_forever()

    def read_metadata(self, reader) -> Entity:
        raw_metadata = reader.schema.metadata[b'meltano']
        raw_metadata = json.loads(raw_metadata.decode("utf-8"))

        return raw_metadata
