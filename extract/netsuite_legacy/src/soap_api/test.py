from .netsuite_soap_client import NetsuiteClient
from .currency import Currency
from .department import Department

def test_client(args):
    # Test the NetsuiteClient Class

    # Initialize an object, set the client, get the wsdl
    print ("1. Initializing the Netsuite client && getting the wsdl")
    client = NetsuiteClient()

    # Check that login works
    if client.login():
        print ("2. Login successful")

        # Test get_record_by_type
        print ("\n3. Sending a simple get request (currency record)")
        result = client.get_record_by_type('currency', 1)

        if result is not None:
            print(result.name, result.displaySymbol)
        else:
            print ("Request failed")

        # Test get_all() call
        print ("\n4. Testing get_all() call")
        entity = Currency(client)
        response = entity.extract_incremental()

        while response is not None and response.status.isSuccess:
            # Transform records
            transform_result = entity.transform(response.recordList.record)
            records = transform_result[0]['data']

            for record in records:
                print('{} | {} | {} | {}'.format(
                        record['internal_id'], record['name'],
                        record['symbol'], record['exchange_rate'])
                )

            response = entity.extract_incremental(searchResult=response)

        # Test search_incremental and search_more calls
        print ("\n5. Testing search_incremental and search_more calls")
        entity = Department(client)

        original_page_size = entity.client.search_preferences['pageSize']
        entity.client.search_preferences['pageSize'] = 10

        response = entity.extract_incremental()

        while response is not None and response.status.isSuccess:
            if response.pageIndex is not None and response.pageIndex > 1:
                print ("\n(..fetching 10 more rows..)")

            # Transform records
            transform_result = entity.transform(response.recordList.record)
            records = transform_result[0]['data']

            for record in records:
                print('{} | {} ({} | {})'.format(
                        record['internal_id'], record['name'],
                        record['parent_id'], record['parent_name'])
                )

            response = entity.extract_incremental(searchResult=response)

        entity.client.search_preferences['pageSize'] = original_page_size
    else:
        print ("2. Could NOT login to account")
