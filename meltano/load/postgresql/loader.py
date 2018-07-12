import logging
import pandas
import io

from abc import ABC, abstractmethod
from meltano.load.base import MeltanoLoader
from meltano.common.db import DB
from meltano.common.service import MeltanoService
from meltano.common.entity import MeltanoEntity
from meltano.common.process import integrate_csv_file # TODO: remove me
from meltano.stream import MeltanoStream


class PostgreSQLLoader(MeltanoLoader):
    def load(self, entity, data):
        logging.info("Received entity {} with data {}.".format(entity, data))

        # this is a hack to use CSV COPY From
        memcsv = io.StringIO()
        data.to_csv(memcsv, index=False)

        with DB.open() as db:
            integrate_csv_file(db, memcsv,
                               primary_key='id',
                               table_name=entity.schema['table_name'],
                               table_schema=entity.schema['schema_name'],
                               update_action="NOTHING")
