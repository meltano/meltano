from elt.schema import Schema, Column, DBType

from schema.utils import columns_from_mappings

PG_SCHEMA = 'netsuite'
PG_TABLE = 'applications'
PRIMARY_KEY = 'unique_id' # TODO: confirm


def describe_schema(args) -> Schema:
    table_name = args.table_name or PG_TABLE
    table_schema = args.schema or PG_SCHEMA

    # curry the Column object
    def column(column_name, data_type, *,
               is_nullable=True,
               is_mapping_key=False):
        return Column(table_schema=table_schema,
                      table_name=table_name,
                      column_name=column_name,
                      data_type=data_type.value,
                      is_nullable=is_nullable,
                      is_mapping_key=is_mapping_key)

    return Schema(table_schema,
        [
          column("unique_id",      DBType.String, is_mapping_key=True),
          column("transaction_id", DBType.Long),
        ] \
        + columns_from_mappings(column, COLUMN_MAPPINGS)  \
        + [ column("imported_at",  DBType.Timestamp) ]
    )


def table_name(args):
    return args.table_name or PG_TABLE


COLUMN_MAPPINGS = [
    {'in': 'line',                'out': 'line', 'type':'Long'},
    {'in': 'amount',              'out': 'amount', 'type':'Double'},
    {'in': 'apply',               'out': 'apply', 'type':'Boolean'},
    {'in': 'applyDate',           'out': 'apply_date', 'type':'Timestamp'},
    {'in': 'currency',            'out': 'currency', 'type':'String'},
    {'in': 'doc',                 'out': 'doc', 'type':'Long'},
    {'in': 'due',                 'out': 'due', 'type':'Double'},
    {'in': 'job',                 'out': 'job', 'type':'String'},
    {'in': 'refNum',              'out': 'ref_num', 'type':'String'},
    {'in': 'total',               'out': 'total', 'type':'Double'},
    {'in': 'type',                'out': 'type', 'type':'String'},

    # VendorPaymentApply
    {'in': 'disc',                'out': 'disc', 'type':'Double'},
    {'in': 'discAmt',             'out': 'disc_amt', 'type':'Double'},
    {'in': 'discDate',            'out': 'disc_date', 'type':'Timestamp'},
]
