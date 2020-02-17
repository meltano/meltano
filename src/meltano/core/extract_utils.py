import aiohttp
import asyncio
import yaml

from sqlalchemy import (
    MetaData,
    Table,
    String,
    Column,
    TIMESTAMP,
    Float,
    Integer,
    Boolean,
    Date,
    REAL,
    SMALLINT,
    TEXT,
    BIGINT,
    JSON,
)
from typing import Generator, Iterator


async def fetch(url, session):
    async with session.get(url) as response:
        if response.status != 200:
            response.raise_for_status()
        return await response.text()


async def get_futures(urls: Iterator[str], timeout=None, headers=None):
    tasks = []
    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        for url in urls:
            task = asyncio.ensure_future(fetch(url, session))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
    return responses


def fetch_urls(
    urls: list, headers: dict = None, timeout: aiohttp.ClientTimeout = None
) -> Iterator[str]:
    """
    Asynchronously fetch multiple urls and return Iterator object that contains all of the responses
    Example usage:
    urls = ['https://httpbin.org/get', 'https://google.com', 'https://gitlab.com/meltano/']
    for result in fetch_urls(urls):
        print(result)

    :param headers: dict of headers to be passed with the request
    :param timeout: timeout object to be passed to the aiohttp lib
    :param urls: Iterator of url strings
    :return: Generator of response texts
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as e:
        # Fix for when asyncio runs inside a sub-thread so there is no
        #  event_loop available
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()

    futures = get_futures(urls=urls, headers=headers, timeout=timeout)
    future = asyncio.ensure_future(futures)
    responses = loop.run_until_complete(future)
    for resp in responses:
        yield resp


def get_sqlalchemy_col(
    column_name: str, column_type_name: str, primary_key_col_name: str
) -> Column:
    """
    Helper method that returns the sqlalchemy Column object to be used for Table def.
    """
    if column_type_name == "timestamp without time zone":
        col = Column(column_name, TIMESTAMP(timezone=False))
    elif column_type_name == "timestamp with time zone":
        col = Column(column_name, TIMESTAMP(timezone=True))
    elif column_type_name == "date":
        col = Column(column_name, Date)
    elif column_type_name == "real":
        col = Column(column_name, REAL)
    elif column_type_name == "integer":
        col = Column(column_name, Integer)
    elif column_type_name == "smallint":
        col = Column(column_name, SMALLINT)
    elif column_type_name == "text":
        col = Column(column_name, TEXT)
    elif column_type_name == "bigint":
        col = Column(column_name, BIGINT)
    elif column_type_name == "float":
        col = Column(column_name, Float)
    elif column_type_name == "boolean":
        col = Column(column_name, Boolean)
    elif column_type_name == "json":
        col = Column(column_name, JSON)
    else:
        col = Column(column_name, String)

    if column_name == primary_key_col_name:
        col.primary_key = True
    return col


def tables_from_manifest(
    manifest_file_path: str, metadata: MetaData, schema_name: str
) -> {str: Table}:
    with open(manifest_file_path) as file:
        schema_manifest: dict = yaml.safe_load(file)
        tables = {}
        for table_name in schema_manifest:
            primary_key_col_name = schema_manifest[table_name]["primary_key"]
            columns: {str: str} = schema_manifest[table_name]["columns"]
            columns_list = [
                get_sqlalchemy_col(column_name, column_type_name, primary_key_col_name)
                for column_name, column_type_name in columns.items()
            ]

            table = Table(table_name, metadata, *columns_list, schema=schema_name)
            tables[table_name] = table
    return tables
