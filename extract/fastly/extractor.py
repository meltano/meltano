import os
import datetime
from typing import Dict
import requests
from dateutil.relativedelta import relativedelta
from pandas import DataFrame
from pandas.io.json import json_normalize
from sqlalchemy import Table, Column, String, MetaData, TIMESTAMP

FASTLY_API_SERVER = "https://api.fastly.com/"
FASTLY_HEADERS = {
    'Fastly-Key': os.getenv("FASTLY_API_TOKEN"),
    'Accept': "application/json",
}

fastly_metadata = MetaData()
line_items = Table(
    'line_items',  # Name of the table
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
    schema='fastly'
)


async def fetch(session, url, headers):
    async with session.get(url, headers=headers) as resp:
        return await resp.json()


class FastlyExtractor:
    """
    Extractor for the Fastly Billing API
    """

    def __init__(self):
        self.name = 'fastly'
        today = datetime.date.today()
        self.this_month = datetime.date(year=today.year, month=today.month, day=1)
        self.start_date = datetime.date(2017, 8, 1)  # after this period billing data starts
        self.entities: list = ['line_items']
        self.primary_keys = {
            'line_items': ['id'],
        }

    def get_billing_urls(self):
        date = self.start_date
        while date < self.this_month:
            billing_endpoint = f'billing/v2/year/{date.year:04}/month/{date.month:02}'
            yield f'{FASTLY_API_SERVER}{billing_endpoint}'
            date += relativedelta(months=1)

    def extract(self) -> Dict[str, DataFrame]:
        for url in self.get_billing_urls():
            resp = requests.get(url, headers=FASTLY_HEADERS)
            yield {
                'line_items': json_normalize(
                    resp.json(),
                    record_path='line_items',
                    meta=['customer_id', 'end_time', 'start_time', 'invoice_id']
                )
            }
