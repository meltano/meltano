import os
import datetime

import grequests
from dateutil.relativedelta import relativedelta
from pandas.io.json import json_normalize
from sqlalchemy import Table, Column, Float, String, MetaData

FASTLY_API_SERVER = "https://api.fastly.com/"
FASTLY_HEADERS = {
    'Fastly-Key': os.getenv("FASTLY_API_TOKEN"),
    'Accept': "application/json"
}


def get_endpoint_url(endpoint) -> str:
    """
    helper function that adds the Fastly domain to the Endpoints that are generated in the body of the class
    :return:
    """
    return f'{FASTLY_API_SERVER}{endpoint}'


fastly_metadata = MetaData()
fastly_billing = Table(
    'fastly_billing',
    fastly_metadata,
    Column('amount', Float),
    Column('id', String, primary_key=True),
)


class FastlyExtractor:
    """
    Extractor for the Fastly Billing API
    """

    def __init__(self):
        self.name = 'fastly'  # used for defining schema name
        today = datetime.date.today()
        self.this_month = datetime.date(year=today.year, month=today.month, day=1)
        # This is historical data starts after this period
        self.start_date = datetime.date(2017, 8, 1)
        self.table: Table = fastly_billing

    def get_billing_urls(self):
        date = self.start_date
        while date < self.this_month:
            billing_endpoint = f'billing/v2/year/{date.year:04}/month/{date.month:02}'
            yield get_endpoint_url(billing_endpoint)
            date += relativedelta(months=1)

    def extract(self):
        rs = (grequests.get(url, headers=FASTLY_HEADERS) for url in self.get_billing_urls())
        results = grequests.imap(rs)
        for result in results:
            result_dict = result.json()
            yield {'line_items': json_normalize(result_dict, record_path='line_items',
                                                meta=['customer_id', 'end_time', 'start_time', 'invoice_id']),
                   # 'regions': json_normalize(result_dict.get('regions')) TODO: figure out how to normalize this part
                   # https://stackoverflow.com/questions/41469430/writing-json-column-to-postgres-using-pandas-to-sql
                   }
