import os
import json
import datetime

import schema.currency as currency_schema
from soap_api.utils import fetch_attribute, merge_transform_results

class Currency:
    schema = currency_schema
    name = 'currency'
    name_plural = 'currencies'


    def __init__(self, netsuite_soap_client):
        # The core soap client used to make all the requests
        self.client = netsuite_soap_client


    def extract(self):
        """
        Extract all the Currency records from NetSuite

        The getAllResult envelope is returned so that status and totalRecords are included
        """
        GetAllRecordType = self.client.core_types_namespace.GetAllRecordType

        currency_record_type = GetAllRecordType('currency')

        return self.client.get_all(currency_record_type)


    def extract_incremental(self, start_time=None, end_time=None, searchResult=None):
        """
        Incremental Extract for looping over search Result pages

        The Currency Entity is a special case that only supports getting all
         records in one go (by using the getAll call)

        So, we fake the incremental extract by getting all in the first run and
         then returning None

        The getAllResult envelope is returned so that status and totalRecords are included
        """
        if searchResult is None:
            return self.extract()
        else:
            # Search has finished
            return None


    def transform(self, records):
        """
        Transform a set of records extracted from NetSuite to be ready to be imported

        NetSuite Records as provided by the API have a lot of Reference records
        or nested structures.

        This method flattens the extracted records and transforms them to
        exactly the schema we need in order to import them in the Data Warehouse

        As results from API calls for a specific entity may have nested support
         entities inside them that we also want to store, this method returns
         a list of all the extracted data and the entities they belong to.

        Returns all the transformed records as a list of {entity, data} dicts.
        e.g. [{'entity': Currency, 'data': ...},
              {'entity': Expenses, 'data': ...}, .. etc ..]
        """
        related_entities = []
        flat_records = []

        for record in records:
            flat_record = {
                "internal_id": record['internalId'],

                "imported_at": datetime.datetime.now().isoformat(),
            }

            # Iterate through all the attributes defined in schema.COLUMN_MAPPINGS
            #  and map each 'in' attribute to the 'out' attribute(s)
            for column_map in self.schema.COLUMN_MAPPINGS:
                # Extract the attributes and data for the given attribute
                extraction_result = fetch_attribute(self, record, column_map)

                # Add the attributes to this entity's record
                flat_record.update( extraction_result['attributes'] )

                # Add the related_entities returned to the rest of the related_entities
                merge_transform_results(related_entities, extraction_result['related_entities'])

            flat_records.append(flat_record)

        # Merge the Current entity's results with the related_entities and return the result
        merge_transform_results(related_entities, [{'entity': Currency, 'data': flat_records}])

        return related_entities
