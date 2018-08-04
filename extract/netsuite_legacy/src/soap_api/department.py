import os
import json
import datetime

import schema.department as department_schema
from soap_api.utils import fetch_attribute, merge_transform_results

class Department:
    schema = department_schema
    name = 'department'
    name_plural = 'departments'


    def __init__(self, netsuite_soap_client):
        # The core soap client used to make all the requests
        self.client = netsuite_soap_client

        self.accounting_namespace = self.client.type_factory(
                'urn:accounting_{}.lists.webservices.netsuite.com'.format(
                    os.getenv("NETSUITE_ENDPOINT")
                )
            )


    def extract(self):
        """
        Extract all the Department records from NetSuite

        Returns all the records found as a list
        """
        DepartmentSearchAdvanced = self.accounting_namespace.DepartmentSearchAdvanced
        department_search = DepartmentSearchAdvanced()

        return self.client.fetch_all_records_for_type(department_search)


    def extract_incremental(self, start_time=None, end_time=None, searchResult=None):
        """
        Incremental Extract for looping over search Result pages

        If called without an initial searchResult, then a new search is initiated
        Otherwise, it follows the previous searchResult's query and fetches the next page.

        The SearchResult envelope is returned (so that status, pageIndex, etc are included)
         or None when the whole process is finished (no more pages to fetch)
        """

        if searchResult is None:
            # New search
            DepartmentSearchAdvanced = self.accounting_namespace.DepartmentSearchAdvanced
            department_search = DepartmentSearchAdvanced()

            return self.client.search_incremental(department_search)
        elif searchResult.status.isSuccess \
          and searchResult.pageIndex is not None \
          and searchResult.totalPages is not None \
          and searchResult.pageIndex < searchResult.totalPages:
            # There are more pages to be fetched
            return self.client.search_more(searchResult)
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
        e.g. [{'entity': Department, 'data': ...},
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
        merge_transform_results(related_entities, [{'entity': Department, 'data': flat_records}])

        return related_entities
