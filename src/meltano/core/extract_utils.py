from __future__ import annotations

import asyncio
from typing import Iterator

import aiohttp
import sqlalchemy
import yaml

STATUS_OK = 200


async def fetch(url, session):
    async with session.get(url) as response:
        if response.status != STATUS_OK:
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
    """Asynchronously fetch multiple urls and return `Iterator` object that contains all of the responses.

    Examples:
        ```python
        urls = ['https://httpbin.org/get', 'https://google.com', 'https://gitlab.com/meltano/']
        for result in fetch_urls(urls):
            print(result)
        ```

    Args:
        headers: Dictionary of headers to be passed with the request.
        timeout: Timeout object to be passed to the aiohttp lib.
        urls: Iterator of url strings.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # Fix for when asyncio runs inside a sub-thread so there is no event loop available
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()

    yield from loop.run_until_complete(
        asyncio.ensure_future(get_futures(urls=urls, headers=headers, timeout=timeout))
    )


SQLALCHEMY_COL_TYPE_NAME_MAP = {
    "timestamp without time zone": sqlalchemy.TIMESTAMP(timezone=False),
    "timestamp with time zone": sqlalchemy.TIMESTAMP(timezone=True),
    "date": sqlalchemy.Date,
    "real": sqlalchemy.REAL,
    "integer": sqlalchemy.Integer,
    "smallint": sqlalchemy.SMALLINT,
    "text": sqlalchemy.TEXT,
    "bigint": sqlalchemy.BIGINT,
    "float": sqlalchemy.Float,
    "boolean": sqlalchemy.Boolean,
    "json": sqlalchemy.JSON,
}


def get_sqlalchemy_col(
    column_name: str, column_type_name: str, primary_key_col_name: str
) -> sqlalchemy.Column:
    """Return the sqlalchemy `Column` object to be used for `Table` definition."""
    col = sqlalchemy.Column(
        column_name,
        SQLALCHEMY_COL_TYPE_NAME_MAP.get(column_type_name, sqlalchemy.String),
    )
    if column_name == primary_key_col_name:
        col.primary_key = True
    return col


def tables_from_manifest(
    manifest_file_path: str, metadata: sqlalchemy.MetaData, schema_name: str
) -> dict[str, sqlalchemy.Table]:
    with open(manifest_file_path) as file:
        schema_manifest: dict = yaml.safe_load(file)
        tables = {}
        for table_name, schema in schema_manifest.items():
            primary_key_col_name = schema["primary_key"]
            columns: dict[str, str] = schema["columns"]
            columns_list = [
                get_sqlalchemy_col(column_name, column_type_name, primary_key_col_name)
                for column_name, column_type_name in columns.items()
            ]
            tables[table_name] = sqlalchemy.Table(
                table_name, metadata, *columns_list, schema=schema_name
            )
    return tables
