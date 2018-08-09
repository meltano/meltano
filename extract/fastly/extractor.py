import os
import datetime
from typing import Dict, Generator

import grequests
from dateutil.relativedelta import relativedelta
from pandas import DataFrame
from pandas.io.json import json_normalize
from sqlalchemy import Table, Column, Float, String, MetaData, Integer, TIMESTAMP, BigInteger

FASTLY_API_SERVER = "https://api.fastly.com/"
FASTLY_HEADERS = {
    'Fastly-Key': os.getenv("FASTLY_API_TOKEN"),
    'Accept': "application/json"
}

fastly_metadata = MetaData()
fastly_billing = Table(
    'fastly_billing',  # Name of the table
    fastly_metadata,
    Column('id', String, primary_key=True),
    Column('aria_invoice_id', String),
    Column('line_number', String),
    Column('description', String),
    Column('service_no', String),
    Column('service_name', String),
    Column('units', String),
    Column('rate_per_unit', String),
    Column('amount', String),
    Column('rate_schedule_no', String),
    Column('rate_schedule_tier_no', String),
    Column('usage_type_no', String),
    Column('usage_type_cd', String),
    Column('plan_no', String),
    Column('plan_name', String),
    Column('client_service_id', String),
    Column('credit_coupon_code', String, nullable=True),
    Column('created_at', TIMESTAMP),
    Column('updated_at', TIMESTAMP),
    Column('deleted_at', TIMESTAMP, nullable=True),
    # Column from the meta of the response
    Column('customer_id', String),
    Column('invoice_id', String),
    Column('start_time', TIMESTAMP),
    Column('end_time', TIMESTAMP),
)


class FastlyExtractor:
    """
    Extractor for the Fastly Billing API
    """

    def __init__(self):
        today = datetime.date.today()
        self.this_month = datetime.date(year=today.year, month=today.month, day=1)
        self.start_date = datetime.date(2017, 8, 1)  # after this period billing data starts
        self.table: Table = fastly_billing
        self.primary_keys: list = ['id']

    def get_billing_urls(self):
        date = self.start_date
        while date < self.this_month:
            billing_endpoint = f'billing/v2/year/{date.year:04}/month/{date.month:02}'
            yield f'{FASTLY_API_SERVER}{billing_endpoint}'
            date += relativedelta(months=1)

    def extract(self) -> Generator[Dict[str, DataFrame], None, None]:
        rs = (grequests.get(url, headers=FASTLY_HEADERS) for url in self.get_billing_urls())
        results = grequests.imap(rs)
        for result in results:
            result_dict = result.json()
            yield {'line_items': json_normalize(result_dict, record_path='line_items',
                                                meta=['customer_id', 'end_time', 'start_time', 'invoice_id']),
                   # 'regions': json_normalize(result_dict.get('regions')) TODO: figure out how to normalize this part
                   # https://stackoverflow.com/questions/41469430/writing-json-column-to-postgres-using-pandas-to-sql
                   }
