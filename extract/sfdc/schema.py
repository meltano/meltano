from sqlalchemy import MetaData, Table, String, Column, TIMESTAMP, Float, Integer

sfdc_metadata = MetaData()
users_table = Table(
    'users',  # Name of the table
    sfdc_metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    schema='sfdc'
)

products_table = Table(
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('price', Float),
    name='products',
    metadata=sfdc_metadata,
    schema='sfdc'
)
carts_table = Table(
    'carts',
    sfdc_metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer),
    Column('product_id', Integer),
    Column('qty', Integer),
    Column('created_at', TIMESTAMP),
    schema='sfdc'
)

pricebookentry = Table(
    Column('id', String, primary_key=True),
    name='products',
    metadata=sfdc_metadata,
    schema='sfdc'
)
import yaml
from con
with open('')
yaml.load()
Date = 'date'
String = 'character varying'
Double = 'real'
Integer = 'integer'
SmallInteger = 'smallint'
BinaryString = 'bytea'
Text = 'text'
Long = 'bigint'
Boolean = 'boolean'
Timestamp = 'timestamp without time zone'
TimestampTZ = 'timestamp with time zone'
JSON = 'json'
ArrayOfInteger = Integer + '[]'
ArrayOfLong = Long + '[]'
ArrayOfString = String + '[]'
UUID = 'UUID'
ArrayOfUUID = UUID + '[]'
