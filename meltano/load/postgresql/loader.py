import logging
import pandas
import io

from abc import ABC, abstractmethod
from elt.db import DB
from elt.load import MeltanoLoader
from elt import MeltanoService, MeltanoEntity
from elt.stream import MeltanoStream
from elt.process import integrate_csv_file # TODO: remove me


class PostgreSQLLoader(MeltanoLoader):
    def load(self, entity, data):
        logging.info("Received entity {} with data {}.".format(entity, data))

        # this is a hack to use CSV COPY From
        memcsv = io.StringIO()
        data.to_csv(memcsv, index=False)

        print(memcsv.getvalue())

        with DB.open() as db:
            integrate_csv_file(db, memcsv,
                               primary_key='name',
                               table_name=entity.schema['table_name'],
                               table_schema=entity.schema['schema_name'],
                               update_action="UPDATE")
