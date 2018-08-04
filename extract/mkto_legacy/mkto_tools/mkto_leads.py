#!/usr/bin/python3
import requests
import config
import logging

from .mkto_token import get_token, mk_endpoint
from .mkto_schema import data_type
from .mkto_utils import handle_marketo_response
from elt.schema import Schema, Column


PG_SCHEMA = 'mkto'
PG_TABLE = 'leads'
PRIMARY_KEY = 'id'


def describe_schema(args) -> Schema:
    source = args.source
    schema = describe_leads()
    fields = schema['result']
    table_name = config.config_table_name(args)
    logging.debug("Table name is: %s" % table_name)

    columns = (column(args.schema, table_name, field) for field in fields)
    columns = list(filter(None, columns))
    columns.sort(key=lambda c: c.column_name)

    return Schema(args.schema, columns)


def describe_leads():
    describe_url = "{}rest/v1/leads/describe.json".format(mk_endpoint)
    payload = {
        "access_token": get_token(),
    }

    response = requests.get(describe_url, params=payload)
    return handle_marketo_response(response)


def get_leads_fieldnames_mkto(lead_description):
    # For comparing what's in Marketo to what's specified in project
    field_names = []
    for item in lead_description.get("result", []):
        if "rest" not in item:
            continue
        name = item.get("rest", {}).get("name")
        if name is None:
            continue
        field_names.append(name)

    return sorted(field_names)


def column(table_schema, table_name, field) -> Column:
    """
    {
    "id": 2,
    "displayName": "Company Name",
    "dataType": "string",
    "length": 255,
    "rest": {
        "name": "company",
        "readOnly": false
    },
    "soap": {
        "name": "Company",
        "readOnly": false
    }
    },
    """
    if 'rest' not in field:
        logging.warning("Missing 'rest' key in %s" % field)
        return None

    column_name = field['rest']['name']
    column_def = column_name.lower()
    dt_type = data_type(field['dataType'])
    is_pkey = column_def == PRIMARY_KEY

    logging.debug("%s -> %s as %s" % (column_name, column_def, dt_type))
    column = Column(table_schema=table_schema,
                    table_name=table_name,
                    column_name=column_def,
                    data_type=dt_type.value,
                    is_nullable=not is_pkey,
                    is_mapping_key=is_pkey,)

    return column
