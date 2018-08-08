import os

from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, TIMESTAMP, Float
from sqlalchemy import create_engine

fastly_metadata = MetaData()

connection_string = f'postgresql://{username}:{password}@{host}:{port}/{db_name}'
engine = create_engine(connection_string)
connection = engine.connect()

fastly_billing = Table(
    'fastly_billing',
    fastly_metadata,
    Column('amount', Float),
    Column('id', String, primary_key=True),
)

from sqlalchemy.dialects.postgresql import insert
import json
from sqlalchemy import Table
import pandas as pd
from pandas.io.json import json_normalize

with open('Extract/fastly/example_fastly_billing_resp.json', 'r') as file:
    d = json.load(file)
    df = json_normalize(d['line_items'])
print(df)
df = df[['amount', 'id']].head()
df = df.to_dict(orient='records')
connection.execute(insert, df)