import pyarrow as pa
import numpy as np
import json

from meltano.common.transform import columnify


class MeltanoStreamWriter:
    def __init__(self, stream, chunksize=10000):
        self.chunksize = chunksize
        self.stream = stream

    def write(self, entity, frame):
        data = self.encode(entity, frame)

        writer = pa.RecordBatchStreamWriter(self._sink, data.schema)
        writer.write_table(data)
        writer.close()

    # TODO: this should be inferred from the Entity at some point
    # there also might be some other transformations that could be done
    # this is the simplest transformation to make it work.
    def normalize_df(self, df):
        """
        Transforms the DataFrame to rename the columns and convert python objects
        to a json representation.
        """
        df.rename(columns=columnify, inplace=True)
        for col, dtype in df.dtypes.items():
            if dtype != np.dtype('object'):
                continue

            xform = lambda x: x if isinstance(x, str) else json.dumps(x)
            df[col] = df[col].map(xform)

        return df

    def encode(self, entity, frame, **metadata):
        page = pa.Table.from_pandas(self.normalize_df(frame),
                                    schema=entity.as_pa_schema(),
                                    preserve_index=False)

        page = page.replace_schema_metadata(metadata={
            'meltano': json.dumps({
                'entity_name': entity.alias,
                'entity_uri': "com.meltano.{}.{}".format("fastly", entity.alias),
            })
        })

        return page

    def open(self):
        self._sink = open(self.stream.fd, 'wb')

    def close(self):
        self._sink.close()
