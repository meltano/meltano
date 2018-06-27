import logging

from xml.etree import ElementTree
from elt.schema import Schema, Column, DBType


data_type_map = {
    'String': DBType.String,
    'Number': DBType.Long,
    'Boolean': DBType.Boolean,
    'Date': DBType.Date
}


def loads(schema_name: str, raw: str) -> Schema:
    tree = ElementTree.fromstring(raw)
    schema = Schema(schema_name)

    sfdc_input_step = tree.find("step[type='SalesforceInput']")
    table_name = sfdc_input_step.find("module").text

    for field in sfdc_input_step.iterfind("fields/field"):
        schema.add_column(
            field_column(schema_name, table_name, field)
        )

    return schema


def field_column(table_schema, table_name, element):
    is_mapping_key = element.find("idlookup").text == "Y"

    return Column(table_schema=table_schema,
                  table_name=table_name,
                  column_name=element.find("field").text,
                  data_type=field_data_type(element).value,
                  is_nullable=not is_mapping_key,
                  is_mapping_key=is_mapping_key)


def field_data_type(element):
    raw_type = element.find("type").text
    raw_format = element.find("format").text

    dt_type = data_type_map[raw_type]

    # date time can have a timezone or not, it depends on the format
    if dt_type == DBType.Date:
        dt_type = dt_type if raw_format == "yyyy-MM-dd" else DBType.Timestamp

    return dt_type
