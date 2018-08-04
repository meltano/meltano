import os
import requests
import json
import logging
import time
import functools

from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport
from zeep.exceptions import Fault

from requests.exceptions import HTTPError, ConnectTimeout

from elt.error import Error

from .account import Account
from .currency import Currency
from .customer import Customer
from .department import Department
from .subsidiary import Subsidiary
from .transaction import Transaction
from .expense import Expense
from .transaction_item import TransactionItem
from .application import Application
from .transaction_line import TransactionLine
from .vendor import Vendor

class NetsuiteClient:
    def __init__(self):
        # The core soap client used to make all the requests
        self.client = self.netsuite_soap_client()

        # Create a type factory for important namespaces used all over the place
        self.core_namespace = self.client.type_factory(
                'urn:core_{}.platform.webservices.netsuite.com'.format(
                    os.getenv("NETSUITE_ENDPOINT")
                )
            )

        self.core_types_namespace = self.client.type_factory(
                'urn:types.core_{}.platform.webservices.netsuite.com'.format(
                    os.getenv("NETSUITE_ENDPOINT")
                )
            )

        self.messages_namespace = self.client.type_factory(
                'urn:messages_{}.platform.webservices.netsuite.com'.format(
                    os.getenv("NETSUITE_ENDPOINT")
                )
            )

        # Create a RecordRef type --> used for almost all calls
        self.RecordRef = self.core_namespace.RecordRef

        # Create the passport and app_info credentials used in all calls
        role = self.RecordRef(internalId=os.getenv("NETSUITE_ROLE"))
        self.passport = self.core_namespace.Passport(email=os.getenv("NETSUITE_EMAIL"),
                        password=os.getenv("NETSUITE_PASSWORD"),
                        account=os.getenv("NETSUITE_ACCOUNT"),
                        role=role)

        self.app_info = self.messages_namespace.ApplicationInfo(applicationId=os.getenv("NETSUITE_APPID"))

        # Create the search preferences for all calls
        self.search_preferences = self.messages_namespace.SearchPreferences(
            bodyFieldsOnly=False,
            returnSearchColumns=False,
            pageSize=100
        )

        # Create the SearchMoreRequest type that will be used for paging by all calls
        self.SearchMoreRequest = self.messages_namespace.SearchMoreRequest

        # Number of failed API requests
        self.failed_api_requests = 0


    def data_center_aware_host_url(self):
        """
        Get the host url for the webservicesDomain used by our Netsuite Account

        Returns the proper host to be used for the NETSUITE_ACCOUNT
        """

        # Let's first try a quick lookup using the REST API
        get_datacenters_url = "https://rest.netsuite.com/rest/datacenterurls?account={}".format(
                                os.getenv("NETSUITE_ACCOUNT")
                              )
        response = requests.get(get_datacenters_url).json()

        try:
            ns_host = response['webservicesDomain']
        except KeyError:
            # If that failed, go the more slow SOAP way
            client = self.netsuite_soap_client(not_data_center_aware=True)

            fpartial = functools.partial(
                           client.service.getDataCenterUrls,
                           os.getenv("NETSUITE_ACCOUNT"),
                       )

            response = self.api_call_with_retry(fpartial)


            if response.body.getDataCenterUrlsResult.status.isSuccess:
                ns_host = response.body.getDataCenterUrlsResult.dataCenterUrls.webservicesDomain
            else:
                # if everything else failed, just use whatever is set for the project
                ns_host = NS_HOST=os.getenv("NETSUITE_HOST")

        return ns_host


    def netsuite_soap_client(self, not_data_center_aware=False):
        if not_data_center_aware:
            ns_host = os.getenv("NETSUITE_HOST")
        else:
            ns_host = self.data_center_aware_host_url()

        # enable cache for a day
        # useful for development and in case of background runners in the future
        cache = SqliteCache(timeout=60*60*24)
        transport = Transport(cache=cache)

        wsdl = "{NS_HOST}/wsdl/v{NS_ENDPOINT}_0/netsuite.wsdl".format(
                    NS_HOST=ns_host,
                    NS_ENDPOINT=os.getenv("NETSUITE_ENDPOINT")
                )

        fpartial = functools.partial(Client, wsdl, transport=transport)

        client = self.api_call_with_retry(fpartial)

        return client


    def login(self):
        fpartial = functools.partial(
            self.client.service.login,
            passport=self.passport,
            _soapheaders={'applicationInfo': self.app_info},
        )

        login = self.api_call_with_retry(fpartial)

        return login.status


    def get_record_by_type(self, type, internal_id):
        """
        Fetch a record given its type as string (e.g. 'account') and its id

        Returns the record or NONE
        """
        record = self.RecordRef(internalId=internal_id, type=type)

        fpartial = functools.partial(
            self.client.service.get,
            record,
            _soapheaders={
                'applicationInfo': self.app_info,
                'passport': self.passport,
            },
        )

        response = self.api_call_with_retry(fpartial)

        r = response.body.readResponse
        if r.status.isSuccess:
            return r.record
        else:
            return None

    def search_incremental(self, search_record):
        """
        Make a simple search request with paging for records of a given type

        The type is provided as a netsuite search type record (e.g. AccountSearch)

        Returns ONLY the records found on the first page of the search results

        The SearchResult envelope is returned (so that status, pageIndex, etc are included)
        """
        fpartial = functools.partial(
            self.client.service.search,
            searchRecord=search_record,
            _soapheaders={
                'searchPreferences': self.search_preferences,
                'applicationInfo': self.app_info,
                'passport': self.passport,
            },
        )

        result = self.api_call_with_retry(fpartial)

        return result.body.searchResult

    def search_more(self, searchResult):
        """
        Fetch more search records while doing an incremental search

        Use the search result from an initial search_incremental call
         or a followup search_more call

        The SearchResult envelope is returned (so that status, pageIndex, etc are included)
        """
        fpartial = functools.partial(
            self.client.service.searchMoreWithId,
            searchId=searchResult.searchId,
            pageIndex=searchResult.pageIndex+1,
            _soapheaders={
                'searchPreferences': self.search_preferences,
                'applicationInfo': self.app_info,
                'passport': self.passport,
            },
        )

        result = self.api_call_with_retry(fpartial)

        return result.body.searchResult


    def fetch_all_records_for_type(self, search_record):
        """
        Fetch all records of a given type

        The type is provided as a netsuite search type record (e.g. AccountSearch)
        The implementation follows a conservative approach and iterates with a
         small pagesize instead of using the maximum allowed pagesize of 2000

        Returns all the records found as a list
        """
        records = []

        searchResult = self.search_incremental(search_record)

        while searchResult.status.isSuccess:
            records.extend(searchResult.recordList.record)

            if searchResult.pageIndex is None \
              or searchResult.totalPages is None \
              or searchResult.pageIndex >= searchResult.totalPages:
                # NO more pages
                break
            else:
                # There are more pages to be fetched
                searchResult = self.search_more(searchResult)

        return records


    def get_all(self, get_all_record_type):
        """
        Retrieve a list of all records of the specified type.

        Records that support the getAll operation are listed in the GetAllRecordType
        e.g. currency, budgetCategory, state, taxAcct, etc

        The getAllResult envelope is returned so that status and totalRecords are included
        """
        fpartial = functools.partial(
            self.client.service.getAll,
            record=get_all_record_type,
            _soapheaders={
                'applicationInfo': self.app_info,
                'passport': self.passport,
            },
        )

        response = self.api_call_with_retry(fpartial)

        return response.body.getAllResult


    def type_factory(self, namespace):
        """
        Helper method for getting a type factory from outside

        Allows consumer classes to write Class.client.type_factory(namespace)
        instead of the ugly Class.client.client.type_factory(namespace)
        """
        return self.client.type_factory(namespace)


    def export_supported_entities(self, only_transactions=False):
        """
        Return a list of initialized objects of main entities

        It is used in the extraction phase in order to dynamically iterate
         over the top level supported entities and extract their data.

        It should be called on an initialized, logged-in NetsuiteClient so that
         all Entities returned are ready to connect and fetch data from the API.

        Support entities are not added in this list as they do not have a
         functional extract operation.
        """
        entities = []

        if only_transactions == False:
            account = Account(self)
            entities.append(account)

            currency = Currency(self)
            entities.append(currency)

            customer = Customer(self)
            entities.append(customer)

            department = Department(self)
            entities.append(department)

            subsidiary = Subsidiary(self)
            entities.append(subsidiary)

            vendor = Vendor(self)
            entities.append(vendor)

        transaction = Transaction(self)
        entities.append(transaction)

        return entities


    def supported_entity_classes():
        """
        Return a list of Classes for all the Entities to be stored in the DW

        It is used in the schema_apply phase in order to dynamically create
         the schema of all supported entities (both top level and support ones)
        """
        entities = [
            Account,
            Application,
            Currency,
            Customer,
            Department,
            Expense,
            Subsidiary,
            Transaction,
            TransactionItem,
            TransactionLine,
            Vendor,
        ]

        return entities


    def supported_entity_class_factory(self, class_name):
        """
        Given an Entity's class name return the Entity's Class

        Return None if the Entity / Class name is not supported
        """
        classes = {
            'Account': Account,
            'Application': Application,
            'Currency': Currency,
            'Customer': Customer,
            'Department': Department,
            'Expense': Expense,
            'Subsidiary': Subsidiary,
            'Transaction': Transaction,
            'TransactionItem': TransactionItem,
            'TransactionLine': TransactionLine,
            'Vendor': Vendor,
        }

        if class_name in classes:
            return classes[class_name]
        else:
            return None


    def api_call_with_retry(self, partial_function):
        sleep_seconds = 30
        max_retries = 20

        try:
            result = partial_function()

            self.failed_api_requests = 0

            return result
        except (HTTPError, ConnectTimeout) as err:
            # Handle HTTP And ConnectTimeout errors
            self.failed_api_requests += 1

            if self.failed_api_requests < max_retries:
                logging.info("Error during API Request: {}".format(err))
                logging.info("({}) Sleeping for {} seconds and trying again.".format(
                                        self.failed_api_requests,
                                        sleep_seconds
                                    )
                )

                time.sleep(sleep_seconds)
                return self.api_call_with_retry(partial_function)

            # Otherwise, report the error and exit
            raise Error("NetSuite Call failed: {}".format(err))
        except Fault as err:
            # Handle NetSuite Supported errors
            self.failed_api_requests += 1

            if self.failed_api_requests < max_retries \
              and ('exceededConcurrentRequestLimitFault' in err.detail[0].tag \
                   or 'exceededRequestLimitFault' in err.detail[0].tag):
                # NetSuite blocked us due to not allowed concurrent connections
                # Wait for the predefined amount of seconds and retry
                logging.info("API Request was blocked due to concurrent request limit.")
                logging.info("({}) Sleeping for {} seconds and trying again.".format(
                                        self.failed_api_requests,
                                        sleep_seconds
                                    )
                )

                time.sleep(sleep_seconds)
                return self.api_call_with_retry(partial_function)

            # Otherwise, report the error and exit
            raise Error("NetSuite Call failed: {}".format(err))
