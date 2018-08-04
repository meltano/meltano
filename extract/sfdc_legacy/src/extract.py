import asyncio
import tempfile
import shutil
import concurrent.futures
import time
import logging

from elt.schema import Schema
from elt.process import upsert_to_db_from_csv
from elt.db import db_open
from salesforce_bulk import SalesforceBulk
from config import config


class Extractor:
    @staticmethod
    def config_from(args):
        return config

    def __init__(self, schema: Schema, args):
        # TODO: granular config
        self.args = args
        self.schema = schema
        self.config = self.config_from(args)

    def connect(self):
        """
        Returns a salesforce-bulk connection.
        """
        return SalesforceBulk(**self.config['connection'])

    def entities(self):
        entities = {}

        for table_name, column_name in self.schema.columns.keys():
            # emit an entity per table
            if not table_name in entities:
                entities[table_name] = []

            entities[table_name].append(column_name)

        return entities


    def extract(self):
        loop = asyncio.get_event_loop()
        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.config['threads']
        )

        tasks = [
            loop.run_in_executor(executor, self.extract_entity, name, attrs) \
            for name, attrs in self.entities().items()
        ]

        files = loop.run_until_complete(
            asyncio.gather(*tasks)
        )

        for entity_name, file_path in files:
            self.process_batch_file(entity_name, file_path)


    def extract_entity(self, entity_name, entity_attrs) -> str:
        """
        Enqueue a batch, await for the completion and return the batch_id.
        """
        client = self.connect()

        logging.info("Creating job for {}...".format(entity_name))
        job = client.create_query_job(entity_name,
                                      contentType='CSV',
                                      concurrency='Parallel')

        try:
            batch = client.query(job, "select {} from {}".format(
                ",".join(entity_attrs),
                entity_name,
            ))
            logging.info("Batch {} created for {}.".format(batch,
                                                           entity_name))
        except Exception as err:
            logging.error("Error creating batch {} for {}: {}".format(batch,
                                                                         entity_name,
                                                                         err))

        client.close_job(job)

        # poll for the status
        while not client.is_batch_done(batch):
            time.sleep(10)

        results = client.get_all_results_for_query_batch(batch, chunk_size=2048)

        try:
            logging.info("Downloading batch {} for {}...".format(batch, entity_name))
            file_path = self.download_batch_results(results)

            return (entity_name, file_path)
        except Exception as err:
            logging.error("Error downloading batch {} for {}: {}".format(batch,
                                                                         entity_name,
                                                                         err),
                              exc_info=True)

    def process_batch_file(self, entity_name, file_path):
        logging.info("Processing {} for {:s}".format(file_path,
                                                     entity_name))



        with db_open() as db:
            upsert_to_db_from_csv(db, file_path,
                                  table_schema=self.args.schema,
                                  table_name=entity_name,
                                  csv_options={
                                      'null': "''",
                                      'force_null': "({columns})", # HACK: as long as we use CSV
                                  },
                                  primary_key='id')

    def download_batch_results(self, results):
        with tempfile.NamedTemporaryFile(delete=False) as out:
            logging.info("\t writing chunks to {}...".format(out.name))
            for r in results:
                shutil.copyfileobj(r, out)
                logging.info("\t ...")

            return out.name
