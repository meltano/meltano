import logging
import pandas
import io

from abc import ABC, abstractmethod
from meltano.load.base import MeltanoLoader
from meltano.common.db import DB
from meltano.common.service import MeltanoService
from meltano.common.entity import Entity
from meltano.common.process import integrate_csv_file # TODO: remove me
from meltano.stream import MeltanoStream


class PostgreSQLLoader(MeltanoLoader):
    def load(self, source_name, entity, data):
        logging.info("Received entity {} with data {}.".format(entity, data))

        # this is a hack to use CSV COPY From
        memcsv = io.StringIO()
        data.to_csv(memcsv, index=False)

        is_pkey = lambda attr: attr.metadata.get('is_pkey', False)

        primary_key = next(ifilter(is_pkey, entity.attributes), None)

        with DB.open() as db:
            integrate_csv_file(db, memcsv,
                               table_schema=source_name,
                               table_name=entity.alias,
                               primary_key=primary_key.name,
                               update_action="NOTHING")
