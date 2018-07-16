import select
import logging
import json
import pyarrow as pa

from meltano.common.entity import MeltanoEntity


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
                metadata = self.read_metadata(reader)
                for batch in reader:
                    loader.load(metadata, batch.to_pandas())
        except Exception as e:
            logging.error("Stream cannot be read: {}".format(e))
        finally:
            loop.stop()

    def read_all(self, loop, loader: 'MeltanoLoader'):
        with open(self.stream.fd, 'rb') as tap:
            loop.add_reader(tap, self.integrate, tap, loader, loop)
            loop.run_forever()

    def read_metadata(self, reader) -> MeltanoEntity:
        raw_metadata = reader.schema.metadata[b'meltano']
        raw_metadata = json.loads(raw_metadata.decode("utf-8"))

        # return self.service.entities[raw_metadata['entity_name']]
        return MeltanoEntity(raw_metadata)
