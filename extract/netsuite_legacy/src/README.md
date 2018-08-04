# NetSuite Extractor

The NetSuite Extractor is part of [Meltano](https://gitlab.com/meltano/meltano).

It is used by Meltano in order to connect to NetSuite, extract Transactions and other relevant entities, normalize the extracted data and load everything to an intermediary schema in a supported Data Warehouse.

At the core of NetSuite Extractor is a SOAP client that connects with NetSuite's SuiteTalk web services, manages the API calls and fetches the data requested by the other processes of the extractor. You can find more details in the [Implementation Details](#implementation-details) section.

In the current version of NetSuite Extractor, all types of supported Transactions are fetched, together with the referenced expenses, transaction items, applications and transaction lines. We also fetch the most important support entities: currencies, departments, subsidiaries and accounts. More details on the entities fetched can be found in the [Reference on NetSuite Entities Fetched](#reference-on-netsuite-entities-fetched) section. Restrictions of the NetSuite Extractor are discussed in the [NetSuite Extractor Restrictions](#netsuite-extractor-restrictions) section.

If you want to add support for more entities or fetch specific types of Transactions as separate first class Entities, check the [How to Update the NetSuite Extractor](#how-to-update-the-netsuite-extractor) section.

## How to use

For setting up and running the Meltano project, follow first the guidelines provided in the [Meltano documentation](https://gitlab.com/meltano/meltano).

The minimum requirements for NetSuite Extractor are Python 3.5 and a running data store (e.g. Postgres) with a database and a user already set. 

### Setup

Variables required by the NetSuite Extractor: 

```
# Standard Meltano Variables
PG_DATABASE=warehouse
PG_USERNAME=warehouse_user
PG_PASSWORD=warehouse_user_password
PG_ADDRESS='localhost'
PG_PORT=5432

# NetSuite Variables
NETSUITE_HOST= 'The default HOST used for contacting the NetSuite Web Services, e.g. https://webservices.netsuite.com'
NETSUITE_ENDPOINT= 'Version of the NetSuite SuiteTalk Endpoint, e.g. 2017_2'
NETSUITE_EMAIL= 'email of the user that will be used to sign-in to NetSuite'
NETSUITE_PASSWORD = 'password of the user that will be used to sign-in to NetSuite'
NETSUITE_ROLE = 'role of the user that will be used to sign-in to NetSuite, e.g. 18'
NETSUITE_ACCOUNT = 'The NetSuite Account the Extractor will connect to'
NETSUITE_APPID = 'The APPID the Extractor will use in order to connect to the provided NetSuite Account'
NETSUITE_EARLIEST_DATE = 'The earliest transaction date to be fetched, e.g. 2018-02-04'
```

Depending on the way the extractor will run, those variables must be provided either as (a) GitLab CI/CD Variables, (b) by using a .env file or (c) as Environment Variables.

Comments on the required variables:
* The NETSUITE_HOST is used only as a fallback: the NetSuite Extractor tries to dynamically fetch the proper HOST based on the provided NETSUITE_ACCOUNT, so a data center aware url is fetched and used by default. 
* The NetSuite Extractor has been developed and tested against the 2017_2 SuiteTalk Endpoint. Working with earlier SuiteTalk Endpoints should require updating the NetsuiteClient Class.
* The ACCOUNT, APPID and user ROLE can be found from NetSuite's web interface (check NetSuite's documentation).
* It is advised to create a new user and a dedicated Integration for connecting with NetSuite Extractor and for monitoring all requests.
* NETSUITE_EARLIEST_DATE is only important for back filling the Data Warehouse with all data stored in NetSuite and will be explained in a following section.

You can test locally that all variables have been set correctly:

1. Clone Meltano
1. Setup [Local environment](https://gitlab.com/meltano/meltano#local-environment)
1. Run the NetSuite Extractor Test

   ```
   python3 elt/netsuite/src/ --schema netsuite test
   ```

The result should be to successfully fetch the NetSuite WSDL, login to the provided account and fetch data using various modes:

```
1. Initializing the Netsuite client && getting the wsdl
2. Login successful

3. Sending a simple get request (currency record)
US Dollar $

4. Testing get_all() call
1 | US Dollar | USD | 1.0
< ... ... more currencies ... >

5. Testing search_incremental and search_more calls
<... Departments for the provided NETSUITE_ACCOUNT...>

(..fetching 10 more rows..)
<... More Departments ...>

(..fetching 10 more rows..)
<... Even More Departments depending on how many there are ...>
```

### Running the NetSuite Extractor with GitLab CI/CD

The following jobs have been defined in Meltano's .gitlab-ci.yml for NetSuite Extractor:
1. netsuite: Automatically runs in the extract stage of the master pipeline. 
   * It applies the NetSuite schema to the Data Warehouse
   * Exports all support entities (e.g. departments and accounts) and transactions updated during the past 3 days
   * Runs a back filling job to fetch 15 days of past transactions not already fetched.  
1. netsuite_manual: The same as (1) but available in branch pipelines as a manual job to test updates for the NetSuite Extractor.
1. netsuite_backlog_manual: Fetch 60 additional days of past transactions not already fetched.

If the master pipeline runs as a scheduled pipeline every couple of hours, the netsuite job makes sure that all latest data from NetSuite are properly fetched and, at the same time, loads past data as time passes. The value of NETSUITE_EARLIEST_DATE is used by the back-filling operation in order to know when to stop making requests for fetching older data.

### Manually extracting data from NetSuite

You can check the options available to NetSuite Extractor by running:

```
python3 elt/netsuite/src/ --help
```

In order to create the default data warehouse schema and the intermediary tables that the extracted NetSuite data will be brought into:

```
python3 elt/netsuite/src/ --schema netsuite apply_schema
```

The same holds in case an extended schema is defined and the existing schema must be updated. _(In all the examples provided, we assume that the schema used is called `netsuite`)_


In order to fetch all support entities (e.g. currencies, departments, accounts, etc) and transactions updated during the past N days:

```
python3 elt/netsuite/src/ --schema netsuite export --days N
```

We fetch Transactions by using the lastModifiedDate attribute, in order to be consistent while incrementally loading data and not miss any update. If you want to use a different approach, please check the [How to Update the NetSuite Extractor](#how-to-update-the-netsuite-extractor) section.

The `export` action fetches all support entities and then Transactions of **all** types for the past N days. 

In order to fetch all support entities and transactions updated during a specific date interval:

```
python3 elt/netsuite/src/ --schema netsuite export -b START_DATE -e END_DATE
```

Where START_DATE, END_DATE are dates in isoformat (YYYY-MM-DD), e.g. `-b 2018-02-26 -e 2018-05-10`. END_DATE is not inclusive, so `-b 2018-02-26 -e 2018-02-27` will only bring transactions last updated at 2018-02-26.


In order to load not already fetched transactions, starting from the earliest lastModifiedDate in the Data Warehouse and going back for N days:

```
python3 elt/netsuite/src/ --schema netsuite backlog --days N
```


Finally, the `extract_type` action fetches the type of each Transaction and updates already fetched Transactions. It is provided only as a recovery operation in case an export job fails in the middle of fetching Transactions and before setting their type.

```
python3 elt/netsuite/src/ --schema netsuite extract_type --days N
python3 elt/netsuite/src/ --schema netsuite extract_type -b START_DATE -e END_DATE
```

## Implementation Details

### NetsuiteClient

NetsuiteClient is a stand alone Netsuite SOAP client, used for connecting with NetSuite SuiteTalk Web Services, fetching the WSDL and running the most common operations provided by SuiteTalk.

At the moment we support the following base NetSuite operations:
*    Fetch data center aware url for provided NETSUITE_ACCOUNT (automatic upon initialization)
*    Connect with NetSuite SuiteTalk Web Services and fetch WSDL (automatic upon initialization)

     ```python
     from soap_api.netsuite_soap_client import NetsuiteClient
     
     ns_client = NetsuiteClient()
     ```

*    [login](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3512617.html) to NetSuite suing provided account details

     ```python
     if ns_client.login():
        # Do something
     else:
        print ("Could NOT login to account")
     ```

*    [get](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3488543.html) single record by type and internal_id

     ```python
     result = ns_client.get_record_by_type('currency', 1)
     
     if result is not None:
        print(result.name, result.displaySymbol)
     ```

*    [getAll](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3489077.html) records of specific recordType

     ```python
     currency_record_type = ns_client.core_types_namespace.GetAllRecordType('currency')
     
     response = ns_client.get_all(currency_record_type)
     
     if response is not None and response.status.isSuccess:
        for record in response.recordList.record:
        # Show results
     ```

*    [search](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3514306.html) and [searchMoreWithId](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3523074.html) operations

     ```python
     accounting_namespace = ns_client.type_factory(
                'urn:accounting_{}.lists.webservices.netsuite.com'.format(
                    os.getenv("NETSUITE_ENDPOINT")
                )
            )
     search_all_departments = accounting_namespace.DepartmentSearchAdvanced()
     
     response = ns_client.search_incremental(search_all_departments)
     
     while response is not None and response.status.isSuccess:
        for record in response.recordList.record:
        # Show results
     
        response = ns_client.search_more(response)
     ```

Additional operations can be added by extending the NetsuiteClient class.

We use [Zeep](http://docs.python-zeep.org/en/master/) as the underlying Python SOAP client. The initialized Zeep client with the proper NetSuite WSDL is available through NetsuiteClient's `client` attribute.

A couple commonly used namespaces (e.g. core, types_core, messages) and types (e.g. RecordRef, SearchMoreRequest) are readily available upon initialization of NetsuiteClient. You can create other namespaces by using the `type_factory(namespace)` call:

```python
ns_client = NetsuiteClient()

# Commonly used namespaces and types
app_info = ns_client.messages_namespace.ApplicationInfo(applicationId=os.getenv("NETSUITE_APPID"))
role = ns_client.RecordRef(internalId=os.getenv("NETSUITE_ROLE"))

# Not preloaded namespace
sales_transactions_namespace = ns_client.type_factory(
                'urn:sales_{}.transactions.webservices.netsuite.com'.format(
                    os.getenv("NETSUITE_ENDPOINT")
                )
            )

transaction_search = sales_transactions_namespace.TransactionSearchAdvanced(
		                criteria={
		                    'basic': {
		                        'lastModifiedDate': {
		                          'operator': 'within',
		                          'searchValue': datetime.date.today() - datetime.timedelta(days=1),
		                          'searchValue2': datetime.date.today(),
		                        },
		                    }
		                }
		            )

yesterday_transactions = ns_client.fetch_all_records_for_type(transaction_search)
```

### Supported Entities

We add each NetSuite Entity that will be supported as a first class citizen by NetSuite Extractor as a separate Class with its own business logic and schema definition.

Entities are defined in `/soap_api/` and their schemas in `/schema/`.

The idea behind this architecture is that each Entity should know how to:
* setup itself (hide details on namespaces used, search parameters, etc).
* define the schema that will be used in our Data Warehouse for the extracted information.
* extract the relevant data from the proper API endpoint.
* transform the extracted data in order to be ready for being stored to our Data Warehouse.
* provide the transformed data and a schema definition to the importer process in order to be [upserted](https://en.wiktionary.org/wiki/upsert) to the Data Warehouse.

Before continuing with the implementation details, such an approach allows us to use any supported Entity in the following code and it will fetch and transform all the relevant data:

```python
# You can replace Department with any other entity (e.g. Account, Subsidiary, etc)
from soap_api.netsuite_soap_client import NetsuiteClient
from soap_api.department import Department

# Initialize Client and Sign-in 
ns_client = NetsuiteClient()

if ns_client.login():
	entity = Department(ns_client)

	# Fetch the first page of results
	response = entity.extract_incremental()

	while response is not None and response.status.isSuccess:
	    #Transform records
	    transform_result = entity.transform(response.recordList.record)
	    records = transform_result[0]['data']

	    for record in records:
	        # Do something with the transformed results

	    # Fetch the next page of results
	    response = entity.extract_incremental(searchResult=response)
```

In order to automate the whole process, each Entity's Class must provide at least the following common interface:
* Initialize itself with a proper, already signed-in, NetsuiteClient that will be used in order to connect to NetSuite and extract relevant data.
* def extract_incremental(self, start_time=None, end_time=None, searchResult=None): Incremental Extract for looping over search Result pages. If searchResult is not provided, a new search is initialized, otherwise the next page of results is requested. 
* def transform(self, records): Transform a set of records extracted from NetSuite to be ready to be imported. The core mapping and any specific business rules for transforming the fetched data are hidden inside this operation.
* schema The entity's schema definition (reference to the definition in /schema/)
* (name, name_plural) attributes for naming created files and other generated objects

The schema definition includes the schema for the table that is used to store the Entity's data and all the column mappings for transforming data fetched from an API Endpoint to the attribute's values that will be inserted to the Data Warehouse. For a more in-depth look into what is happening check an Entity's schema file (e.g. `/schema/account.py`) and the `columns_from_mappings` function in `/schema/utils.py`.

In addition, there are a couple of support Entities that are provided as nested structures when fetching data for core Entities, which will not be further discussed in this documentation. As an example, when fetching Transactions, nested lists of Transaction Lines, Items or Expenses are also fetched for some Transaction Types. Those are automatically generated from the parent record, transformed and imported to our Data Warehouse. 

As a result, the full supported extraction pipeline allows for a single source (API Call) to generate multiple Entities and, as a result, multiple tables in the Data Warehouse with references between them. For an example on how this is orchestrated check the Transaction Class and the support [TransactionLine, TransactionItem, Expense, Application] classes.

Finally everything is tied together and is automated by letting the NetsuiteClient Class know which are the supported Entities to be imported in the Data Warehouse and which of those are primary Entities to be used illiterately for extracting data from the Endpoints:
* NetsuiteClient.supported_entity_classes(): All Entities to be imported to the Data Warehouse (i.e. create a schema for them)
* NetsuiteClient.export_supported_entities(self): Initialized objects of primary Entities to be used by the exporter for extracting data. 

### NetSuite Extractor

Two core operations (actions) are supported by the NetSuite Extractor: apply_schema and export

With apply_schema, we can generate or update the schema for all supported Entities, as defined by NetsuiteClient.supported_entity_classes()

The export action manages the whole [ Extract Data -> Transform -> Load in the Data Warehouse ] pipeline: 
* Iterate through all primary Entities, as defined by ns_client.export_supported_entities().
* For each primary Entity, run the incremental extraction / transform loop until no more data remain to be fetched.
* The intermediary results from each iteration, further separated for each entity generated in case of a (one API call)-to-(many Entities) case, are stored in temporary files
* The temporary export files are yielded to import processes that fetch them and upsert the data to the Data Warehouse. 

## How to Update the NetSuite Extractor

NetSuite Extractor at its current version supports the core functionality required for fetching data useful to GitLab, so a lot of NetSuite Entities and API Operations are not supported yet. The purpose of this section is to provide guidance on how to add new Entities as first class citizens and how to add new operations to NetsuiteClient.

### How to Add a new Supported Entity

(1) Find the Entity to be supported in NetSuite's documentation

[SuiteTalk Web Services Supported Records](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3635369.html)

Check the type of operation used to fetch records (search vs getAll vs a new operation that needs to be added in NetsuiteClient).

[SuiteTalk Web Services Available Operations](https://system.netsuite.com/app/help/helpcenter.nl?fid=chapter_N3477815.html)

Check the [Schema Browser](http://www.netsuite.com/help/helpcenter/en_US/srbrowser/Browser2017_2/schema/index.html) for the entry.

(2) Create the schema file for the entity

You can start from scratch or work based on the code of a similar entity:

```
cp elt/netsuite/src/schema/department.py elt/netsuite/src/schema/xxxxxx.py
```

All the columns to be supported must be added in the COLUMN_MAPPINGS list, together with their Data Type.


(3) Create the Class for the Entity

A simple Entity with a similar extraction mechanism is a good point to start. For example Department is the simplest one that uses the search and searchMoreWithId calls:

```
cp elt/netsuite/src/soap_api/department.py elt/netsuite/src/soap_api/xxxxxx.py
```

Add any specific namespaces, types and business logic required for the newly introduced Entity

(4) Make NetsuiteClient aware of the newly introduced Entity

Add import on the top of `soap_api/netsuite_soap_client.py`.

Add the Entity to:
* def export_supported_entities(self, only_transactions=False)
* def supported_entity_classes()
* def supported_entity_class_factory(self, class_name)

In case of a support Entity (e.g. for Transactions), updating the parent's schema definition (e.g. transaction_config.py) is also needed:
* Add the Entity to the COLUMN_MAPPINGS for the parent Entity with an 'ENTITY_LIST' data type
* Add Entity to the RELATED_ENTITIES for the parent Entity

### How to Add a new API Call / Operation

In case a new API Call must be added, check the [SuiteTalk Web Services Available Operations](https://system.netsuite.com/app/help/helpcenter.nl?fid=chapter_N3477815.html) and add it in the NetsuiteClient through a wrapper function. 

Implementation detail: All API calls run through the NetsuiteClient.api_call_with_retry(self, partial_function) in order to catch errors, retry in case of known issues or fail gracefully. Check and update with any errors that must be supported and custom behaviors for those cases.

### How to Add new actions to NetSuite Extractor and update/add CI jobs

New actions for the NetSuite Extractor can be added in `src/__main__.py`.

Those actions can be added to one of the currently defined NetSuite jobs in .gitlab-ci.yml or in new jobs for your pipelines.

Check the [Running the NetSuite Extractor with GitLab CI/CD](#running-the-netsuite-extractor-with-gitlab-cicd) section for more details.

# NetSuite Extractor Restrictions 

There are some limitations in the NetSuite API, especially when fetching Transactions. 

NetSuite Extractor can fetch almost all types of Transactions also available in NetSuite's Online interface, except:
* Transfers between accounts
* Credit Card Transactions
* Currency Revaluation Transactions

# Reference on NetSuite Entities Fetched

In the following subsections, the Entities fetched from NetSuite are described. We assume that the schema used is `netsuite`. 

The schema for the intermediary table in the Data Warehouse and the transformation rules used in order to map the extracted data to that schema can be found for each entity in the related schema definition file under `/elt/netsuite/src/schema/` (e.g. schema/department.py for departments).

The tables for all entities have at least the `(internal_id, external_id)` for each record and an `imported_at` timestamp for marking the last time the record was imported/updated.

## Entity: Currency

Currencies are very simple entities that are fetched all at once by using the [getAll](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3489077.html) call.

All Currencies are fetched and updated each time the `export` operation runs.

Details:
* SuiteTalk Documentation: [Currency](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3741577.html)
* NetSuite Extractor Class: Currency
* Data Warehouse Intermediary Table: netsuite.currencies

## Entity: Department

Departments are fetched by using the [search](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3514306.html) and [searchMore](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3522244.html) calls.

All Departments are fetched and updated each time the `export` operation runs.

Details:
* SuiteTalk Documentation: [Department](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3742370.html)
* NetSuite Extractor Class: Department
* Data Warehouse Intermediary Table: netsuite.departments

## Entity: Subsidiary

Subsidiaries are fetched by using the [search](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3514306.html) and [searchMore](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3522244.html) calls.

All Subsidiaries are fetched and updated each time the `export` operation runs.

Details:
* SuiteTalk Documentation: [Subsidiary](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3754626.html)
* NetSuite Extractor Class: Subsidiary
* Data Warehouse Intermediary Table: netsuite.subsidiaries

## Entity: Account

Accounts are fetched by using the [search](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3514306.html) and [searchMore](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3522244.html) calls.

All Accounts are fetched and updated each time the `export` operation runs.

Details:
* SuiteTalk Documentation: [Account](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3739999.html)
* NetSuite Extractor Class: Account
* Data Warehouse Intermediary Table: netsuite.accounts

## Entity: Transaction

Transactions are the most important entity in NetSuite. There are [~40 types](http://www.netsuite.com/help/helpcenter/en_US/srbrowser/Browser2017_2/schema/enum/transactiontype.html?mode=package) of transactions that can be fetched using the [search](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3514306.html) and [searchMore](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3522244.html) calls.

In NetSuite Extractor we have decided to fetch transactions of **all** types in one really large 300+ attribute table. Our focus was to facilitate more effective processing and mass transformations for all transactions at once in later steps. This can of course be updated by extending the NetSuite Extractor with additional supported entities, one for each Transaction Type of interest, as described in the [How to Update the NetSuite Extractor](#how-to-update-the-netsuite-extractor) section. 

In the current implementation, each transaction record is differentiated by the value of the `transaction_type` attribute by using the [types](http://www.netsuite.com/help/helpcenter/en_US/srbrowser/Browser2017_2/schema/enum/transactiontype.html?mode=package) provided by NetSuite.

Details:
* SuiteTalk Documentation: [All Transaction Types](https://system.netsuite.com/app/help/helpcenter.nl?fid=chapter_N3657735.html)
* NetSuite Extractor Class: Transaction
* Data Warehouse Intermediary Table: netsuite.transactions

## Entity: Expense

For Transactions types that include expenses, each expense (line) is stored in a separate table with the transaction_id and a line number.  

Those entities are automatically extracted from the parent Transaction and exported while processing the Transactions that have nested expense lists in their Search Response. 

_In the current implementation, the referenced Expense Lists are also stored as JSON strings in the record for the Transaction that included them_

Details:
* NetSuite Extractor Class: Expense
* Data Warehouse Intermediary Table: netsuite.expenses

## Entity: TransactionItem

For Transactions types that include items, each item (line) is stored in a separate table with the transaction_id and a line number.

Those entities are automatically extracted from the parent Transaction and exported while processing the Transactions that have nested item lists in their Search Response. 

_In the current implementation, the referenced Item Lists are also stored as JSON strings in the record for the Transaction that included them_
  
Details:
* NetSuite Extractor Class: TransactionItem
* Data Warehouse Intermediary Table: netsuite.transaction_items

## Entity: Application

For Transactions types that include Applications, each application (line) is stored in a separate table with the transaction_id and a line number.

Those entities are automatically extracted from the parent Transaction and exported while processing the Transactions that have nested application lists in their Search Response. 

_In the current implementation, the referenced Application Lists are also stored as JSON strings in the record for the Transaction that included them_

Details:
* NetSuite Extractor Class: Application
* Data Warehouse Intermediary Table: netsuite.applications

## Entity: TransactionLine

For Transactions types (e.g. journal entries) that include Transaction Lines, each line is stored in a separate table with the transaction_id and a line number.

Those entities are automatically extracted from the parent Transaction and exported while processing the Transactions that have nested Transaction Line lists in their Search Response. 

_In the current implementation, the referenced TransactionLine Lists are also stored as JSON strings in the record for the Transaction that included them_

Details:
* NetSuite Extractor Class: TransactionLine
* Data Warehouse Intermediary Table: netsuite.transaction_lines


# External References for NetSuite SuiteTalk Web Services

## Publicly available

[SuiteTalk Documentation](http://www.netsuite.com/portal/developers/resources/suitetalk-documentation.shtml)

[SuiteTalk Schema Browser - 2017_02 Endpoint](http://www.netsuite.com/help/helpcenter/en_US/srbrowser/Browser2017_2/schema/index.html)

[WSDL for 2017_02 Endpoint](https://webservices.netsuite.com/wsdl/v2017_2_0/netsuite.wsdl)

## Require NetSuite Sign-in

[SuiteTalk Web Services Documentation](https://system.netsuite.com/app/help/helpcenter.nl?fid=book_N3412393.html)

[SuiteTalk Web Services Supported Records](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3635369.html)

[SuiteTalk Web Services Available Operations](https://system.netsuite.com/app/help/helpcenter.nl?fid=chapter_N3477815.html)

Dynamic Discovery of HOST URL:
* [Dynamic Discovery of URLs for Web Services and RESTlet Clients](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N240322.html#bridgehead_N240435)
* [DataCenterUrls REST Service](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_1498473223.html)
* [getDataCenterUrls](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3494684.html)

Searching for Transactions:
* [General Search Documentation](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3514306.html)
* [Transaction Search](https://system.netsuite.com/app/help/helpcenter.nl?fid=section_N3659492.html)
* [Transaction Entities](https://system.netsuite.com/app/help/helpcenter.nl?fid=chapter_N3657735.html)
* [Schema Browser - TransactionSearch - 2017_02](https://system.netsuite.com/help/helpcenter/en_US/srbrowser/Browser2017_2/schema/search/transactionsearch.html?mode=package)
* [Available Transaction Types for search](http://www.netsuite.com/help/helpcenter/en_US/srbrowser/Browser2017_2/schema/enum/transactiontype.html?mode=package)

# Contributing to NetSuite Extractor

We welcome contributions and improvements, please see the [contribution guidelines](https://gitlab.com/meltano/meltano/blob/master/CONTRIBUTING.md) for Meltano.

# License

This code is distributed under the MIT license, see the [LICENSE](https://gitlab.com/meltano/meltano/blob/master/LICENSE) file.
