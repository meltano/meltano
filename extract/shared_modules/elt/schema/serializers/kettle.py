import logging

from xml.etree import ElementTree
from elt.schema import Schema, Column, DBType
from .base import Serializer


data_type_map = {
    'String': DBType.String,
    'Number': DBType.Double,
    'Boolean': DBType.Boolean,
    'Date': DBType.Date,
    'Integer': DBType.Long,
}


class KettleSerializer(Serializer):
    def loads(self, raw: str) -> Schema:
        tree = ElementTree.fromstring(raw)

        sfdc_input_step = tree.find("step[type='SalesforceInput']")
        table_name = sfdc_input_step.find("module").text

        for field in sfdc_input_step.iterfind("fields/field"):
            self.schema.add_column(
                self.field_column(table_name, field)
            )

        return self


    def field_column(self, table_name, element):
        is_mapping_key = element.find("idlookup").text == "Y"

        return Column(table_schema=self.schema.name,
                    table_name=table_name,
                    column_name=element.find("field").text,
                    data_type=self.field_data_type(element).value,
                    is_nullable=not is_mapping_key,
                    is_mapping_key=is_mapping_key)


    def field_data_type(self, element):
        raw_type = element.find("type").text
        raw_format = element.find("format").text

        dt_type = data_type_map[raw_type]

        # either a `date` or a `timestamp`: it depends on the format
        if dt_type == DBType.Date:
            dt_type = dt_type if raw_format == "yyyy-MM-dd" else DBType.Timestamp

        return dt_type
