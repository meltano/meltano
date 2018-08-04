from elt.schema import Schema, Column, DBType

from schema.utils import columns_from_mappings

PG_SCHEMA = 'netsuite'
PG_TABLE = 'accounts'
PRIMARY_KEY = 'internal_id' # TODO: confirm


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
        [ column("internal_id", DBType.Long, is_mapping_key=True) ]  \
        + columns_from_mappings(column, COLUMN_MAPPINGS)  \
        + [ column("imported_at", DBType.Timestamp) ]
    )


def table_name(args):
    return args.table_name or PG_TABLE


COLUMN_MAPPINGS = [
    {'in': 'externalId',              'out': 'external_id', 'type':'String'},
    {'in': 'acctName',                'out': 'acct_name', 'type':'String'},
    {'in': 'acctNumber',              'out': 'acct_number', 'type':'String'},
    {'in': 'acctType',                'out': 'acct_type', 'type':'String'},
    {'in': 'billableExpensesAcct',    'out': 'billable_expenses_acct', 'type':'RecordRef'},
    {'in': 'cashFlowRate',            'out': 'cash_flow_rate', 'type':'String'},
    {'in': 'category1099misc',        'out': 'category1099misc', 'type':'RecordRef'},
    {'in': 'class',                   'out': 'class', 'type':'RecordRef'},
    {'in': 'curDocNum',               'out': 'cur_doc_num', 'type':'Long'},
    {'in': 'currency',                'out': 'currency', 'type':'RecordRef'},
    {'in': 'deferralAcct',            'out': 'deferral_acct', 'type':'RecordRef'},
    {'in': 'department',              'out': 'department', 'type':'RecordRef'},
    {'in': 'description',             'out': 'description', 'type':'String'},
    {'in': 'eliminate',               'out': 'eliminate', 'type':'Boolean'},
    {'in': 'exchangeRate',            'out': 'exchange_rate', 'type':'String'},
    {'in': 'generalRate',             'out': 'general_rate', 'type':'String'},
    {'in': 'includeChildren',         'out': 'include_children', 'type':'Boolean'},
    {'in': 'inventory',               'out': 'inventory', 'type':'Boolean'},
    {'in': 'isInactive',              'out': 'is_inactive', 'type':'Boolean'},
    {'in': 'legalName',               'out': 'legal_name', 'type':'String'},
    {'in': 'location',                'out': 'location', 'type':'RecordRef'},
    {'in': 'openingBalance',          'out': 'opening_balance', 'type':'Double'},
    {'in': 'parent',                  'out': 'parent', 'type':'RecordRef'},
    {'in': 'restrictToAccountingBookList', 'out': 'restrict_to_accounting_book_list', 'type':'RecordRefList'},
    {'in': 'revalue',                 'out': 'revalue', 'type':'Boolean'},
    {'in': 'subsidiaryList',          'out': 'subsidiary_list', 'type':'RecordRefList'},
    {'in': 'tranDate',                'out': 'tran_date', 'type':'Timestamp'},
    {'in': 'unit',                    'out': 'unit', 'type':'RecordRef'},
    {'in': 'unitsType',               'out': 'units_type', 'type':'RecordRef'},
    {'in': 'customFieldList',         'out': 'custom_field_list', 'type':'CustomFieldList'},
]

