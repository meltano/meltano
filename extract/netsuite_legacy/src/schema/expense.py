from elt.schema import Schema, Column, DBType

from schema.utils import columns_from_mappings

PG_SCHEMA = 'netsuite'
PG_TABLE = 'expenses'
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
    {'in': 'account',             'out': 'account', 'type':'RecordRef'},
    {'in': 'amount',              'out': 'amount', 'type':'Double'},
    {'in': 'grossAmt',            'out': 'gross_amt', 'type':'Double'},
    {'in': 'isBillable',          'out': 'is_billable', 'type':'Boolean'},
    {'in': 'department',          'out': 'department', 'type':'RecordRef'},
    {'in': 'category',            'out': 'category', 'type':'RecordRef'},
    {'in': 'memo',                'out': 'memo', 'type':'String'},
    {'in': 'tax1Amt',             'out': 'tax1_amt', 'type':'Double'},
    {'in': 'taxAmount',           'out': 'tax_amount', 'type':'Double'},
    {'in': 'taxCode',             'out': 'tax_code', 'type':'RecordRef'},
    {'in': 'taxDetailsReference', 'out': 'tax_details_reference', 'type':'String'},
    {'in': 'taxRate1',            'out': 'tax_rate1', 'type':'Double'},
    {'in': 'taxRate2',            'out': 'tax_rate2', 'type':'Double'},
    {'in': 'amortizationEndDate', 'out': 'amortization_end_date', 'type':'Timestamp'},
    {'in': 'amortizationResidual', 'out': 'amortization_residual', 'type':'String'},
    {'in': 'amortizationSched',   'out': 'amortization_sched', 'type':'RecordRef'},
    {'in': 'amortizStartDate',    'out': 'amortiz_start_date', 'type':'Timestamp'},
    {'in': 'class',               'out': 'class', 'type':'RecordRef'},
    {'in': 'customer',            'out': 'customer', 'type':'RecordRef'},
    {'in': 'location',            'out': 'location', 'type':'RecordRef'},
    {'in': 'markReceived',        'out': 'mark_received', 'type':'Boolean'},
    {'in': 'orderDoc',            'out': 'order_doc', 'type':'Long'},
    {'in': 'orderLine',           'out': 'order_line', 'type':'Long'},
    {'in': 'projectTask',         'out': 'project_task', 'type':'RecordRef'},

    # PurchaseOrderExpense
    {'in': 'createdFrom',         'out': 'created_from', 'type':'RecordRef'},
    {'in': 'isClosed',            'out': 'is_closed', 'type':'Boolean'},
    {'in': 'linkedOrderList',     'out': 'linked_order_list', 'type':'RecordRefList'},
    {'in': 'customFieldList',     'out': 'custom_field_list', 'type':'CustomFieldList'},
]
