import io
import os
import logging
import pandas as pd
import numpy as np
import json
import aiohttp
import asyncio
import itertools

from pandas.io.json import json_normalize
from meltano.schema import DBType
from meltano.extract.base import MeltanoExtractor
from meltano.common.transform import columnify
from meltano.common.service import MeltanoService
from meltano.common.entity import Entity, Attribute, TransientAttribute


URL = "https://api.fastly.com/"


# TODO: refactor to utils
pandas_to_dbtype = {
    np.dtype('object'): DBType.String,
    np.dtype('float64'): DBType.Double,
    np.dtype('float32'): DBType.Double,
    np.dtype('int64'): DBType.Long,
    np.dtype('int32'): DBType.Integer,
    np.dtype('bool'): DBType.Boolean,
    np.dtype('int8'): DBType.Integer,
    np.dtype('datetime64'): DBType.Timestamp
}


# TODO: refactor to utils
def df_to_entity(alias, df):
    """
    Infer an Entity from a DataFrame
    """
    attrs = []
    for column, dtype in df.dtypes.items():
        converted_type = pandas_to_dbtype[dtype]
        input = TransientAttribute(column, converted_type.value)
        output = TransientAttribute(columnify(column), converted_type.value)

        attrs.append(
            Attribute(column, input, output)
        )

    return Entity(alias, attributes=attrs)


class FastlyExtractor(MeltanoExtractor):
    """
    Extractor for the Fastly Billing API
    """

    source_name = "fastly"


    def create_session(self):
        headers = {
            'Fastly-Key': os.getenv("FASTLY_API_TOKEN"),
            'Accept': "application/json"
        }
        session = aiohttp.ClientSession(headers=headers)
        return session


    def url(self, endpoint):
        return "".join((URL, endpoint))


    # TODO: refactor this out in a HTTP loader
    async def req(self, session, endpoint, payload={}):
        url = self.url(endpoint)
        async with session.get(url) as resp:
            logging.debug("API {}:{}".format(url, resp.status))
            if resp.status != 200:
                raise resp.status

            return json_normalize(await resp.json())


    async def entities(self):
        """
        Generates a list of Entity object for entity auto-discovery
        """
        async with self.create_session() as session:
            billing = await self.req(session, "billing/v2/year/2018/month/06")
            yield df_to_entity("Billing", billing)


    # TODO: refactor this out in a discovery component
    def discover_entities(self):
        async def drain(generator):
            results = []
            async for result in generator:
                results.append(result)
            return results

        loop = asyncio.get_event_loop()
        entities = loop.run_until_complete(
            drain(self.entities())
        )

        return entities


    async def extract(self, entity):
        async with self.create_session() as session:
            for year, month in itertools.product(range(2017, 2018),
                                                 range(1, 12)):
                url = "billing/v2/year/{:04}/month/{:02}".format(year, month)

                try:
                    yield await self.req(session, url)
                except Exception as err:
                    logging.error(err)
