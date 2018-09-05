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


def fetch_urls(urls: list, headers: dict = None, timeout: aiohttp.ClientTimeout = None) -> Iterator[str]:
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
    loop = asyncio.get_event_loop()
    futures = get_futures(
        urls=urls,
        headers=headers,
        timeout=timeout,
    )
    future = asyncio.ensure_future(futures)
    responses = loop.run_until_complete(future)
    for resp in responses:
        yield resp


def get_sqlalchemy_col(field_name: str, field_type_name: str) -> Column:
    if field_type_name == 'timestamp without time zone':
        return Column(field_name, TIMESTAMP(timezone=False))
    elif field_type_name == 'timestamp with time zone':
        return Column(field_name, TIMESTAMP(timezone=True))
    elif field_type_name == 'character varying':
        return Column(field_name, String)
    elif field_type_name == 'date':
        return Column(field_name, Date)
    elif field_type_name == 'real':
        return Column(field_name, REAL)
    elif field_type_name == 'integer':
        return Column(field_name, Integer)
    elif field_type_name == 'smallint':
        return Column(field_name, SMALLINT)
    elif field_type_name == 'text':
        return Column(field_name, TEXT)
    elif field_type_name == 'bigint':
        return Column(field_name, BIGINT)
    elif field_type_name == 'float':
        return Column(field_name, Float)
    elif field_type_name == 'boolean':
        return Column(field_name, Boolean)
    elif field_type_name == 'json':
        return Column(field_name, JSON)
    # elif field_type_name == '':
    #     return Column(field_name, )
    print((f'{field_type_name} is unknown column type'))
    raise NotImplemented


def tables_from_manifest(
        manifest_file_path: str,
        metadata: MetaData,
        schema_name: str,
) -> {str: Table}:
    with open(manifest_file_path) as file:
        schema_manifest: dict = yaml.load(file)
        tables = {}
        for table_name in schema_manifest:
            columns: {str: str} = schema_manifest[table_name]['columns']
            columns_list = [
                get_sqlalchemy_col(field_name, field_type_name)
                for field_name, field_type_name in columns.items()
            ]
            table = Table(
                table_name,
                metadata,
                *columns_list,
                schema=schema_name,
            )
            tables[table_name] = table
    return tables
