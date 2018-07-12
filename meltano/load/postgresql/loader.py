import logging
import pandas
import io

from abc import ABC, abstractmethod
from meltano.db import DB
from meltano.load import MeltanoLoader
from meltano import MeltanoService, MeltanoEntity
from meltano.stream import MeltanoStream
from meltano.process import integrate_csv_file # TODO: remove me


class PostgreSQLLoader(MeltanoLoader):
    def load(self, entity, data):
        logging.info("Received entity {} with data {}.".format(entity, data))

        # this is a hack to use CSV COPY From
        memcsv = io.StringIO()
        data.to_csv(memcsv, index=False)

        with DB.open() as db:
            integrate_csv_file(db, memcsv,
                               primary_key=entity.primary_key,
                               table_name=entity.table_name,
                               table_schema=entity.schema_name,
                               update_action=update_action)
