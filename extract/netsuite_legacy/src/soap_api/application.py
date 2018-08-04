import os
import json
import datetime

import schema.application as application_schema
from soap_api.utils import fetch_attribute

class Application:
    """
    Support Enity Class for handling and storing Application Lists

    It is not used to directly extract data from NetSUite, just fetch Application
     List data when when extracting a Transaction, transform them and store
     them to the DW together with a transaction_id reference.

    As a support Entity, it does not directly extract data and does not need a client
    So we are skipping the initialization and the extract/extract_incremental definitions
    """

    schema = application_schema
    name = 'application'
    name_plural = 'applications'


    def transform(self, records, parent_id):
        """
        Transform a set of Application records fetched from a Transaction

        The Transaction's internal_id is provided in parent_id

        Following the transform interface for all Entities, it returns
         a list of {'entity': , data:} dictionaries.

        In this case, as it is a support Entity, it just returns one entry:
         [{'entity': Application, 'data': transformedrecords}]
        """
        flat_records = []

        for record in records:
            flat_record = {
                # Unfortunately, line numbers always return as 0 for applications
                # Generating a pretty unique key
                "unique_id": "{}.{}.{}".format(parent_id, record['doc'], record['due']),

                "transaction_id": parent_id,
                "imported_at": datetime.datetime.now().isoformat(),
            }

            # Iterate through all the attributes defined in schema.COLUMN_MAPPINGS
            #  and map each 'in' attribute to the 'out' attribute(s)
            for column_map in self.schema.COLUMN_MAPPINGS:
                extraction_result = fetch_attribute(self, record, column_map)

                # Only keep the attributes for Support Entities
                # No nested attributes inside other nested attributes supported
                flat_record.update( extraction_result['attributes'] )

            flat_records.append(flat_record)

        return [{'entity': Application, 'data': flat_records}]
