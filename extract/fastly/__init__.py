import asyncio
import os
import datetime

import aiohttp
from dateutil.relativedelta import relativedelta
import pandas as pd
from pandas import DataFrame
from pandas.io.json import json_normalize
from sqlalchemy import Table, Column, String, MetaData, TIMESTAMP

REQUEST_TIMEOUT_SEC = 30
CONNECTIONS_LIMIT = 100
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
    Column('start_time', TIMESTAMP, nullable=True),
    Column('end_time', TIMESTAMP, nullable=True),
    schema='fastly'
)


async def fetch(url, session):
    async with session.get(url) as response:
        if response.status != 200:
            response.raise_for_status()
        return await response.json()


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
        self.tables = {
            'line_items': line_items
        }
        self.primary_keys = {
            'line_items': ['id'],
        }

    def get_billing_urls(self):
        urls = []
        date = self.start_date
        while date < self.this_month:
            billing_endpoint = f'billing/v2/year/{date.year:04}/month/{date.month:02}'
            urls.append(f'{FASTLY_API_SERVER}{billing_endpoint}')
            date += relativedelta(months=1)
        return urls

    async def run(self):
        tasks = []
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SEC)
        async with aiohttp.ClientSession(headers=FASTLY_HEADERS, timeout=timeout) as session:
            for url in self.get_billing_urls():
                task = asyncio.ensure_future(fetch(url, session))
                tasks.append(task)
            responses = await asyncio.gather(*tasks)
        return responses

    def extract(self, entity_name):
        if entity_name == 'line_items':
            loop = asyncio.get_event_loop()
            future = asyncio.ensure_future(self.run())
            responses = loop.run_until_complete(future)
            for resp in responses:
                df = json_normalize(
                    resp,
                    record_path='line_items',
                    # TODO: generate from the Table def
                    meta=['customer_id', 'invoice_id', 'end_time', 'start_time'],
                )
                datetime_cols = ['created_at', 'deleted_at', 'updated_at', 'end_time', 'start_time']
                # TODO: generate datetime cols from the Table def
                df[datetime_cols].apply(pd.to_datetime)
                yield df
