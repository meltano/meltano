from elt.schema import Schema, Column, DBType

from schema.utils import columns_from_mappings

PG_SCHEMA = 'netsuite'
PG_TABLE = 'transaction_lines'
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
    {'in': 'line',                    'out': 'line', 'type':'Long'},
    {'in': 'account',                 'out': 'account', 'type':'RecordRef'},
    {'in': 'credit',                  'out': 'credit', 'type':'Double'},
    {'in': 'creditTax',               'out': 'credit_tax', 'type':'Double'},
    {'in': 'debit',                   'out': 'debit', 'type':'Double'},
    {'in': 'debitTax',                'out': 'debit_tax', 'type':'Double'},
    {'in': 'department',              'out': 'department', 'type':'RecordRef'},
    {'in': 'entity',                  'out': 'entity', 'type':'RecordRef'},
    {'in': 'memo',                    'out': 'memo', 'type':'String'},
    {'in': 'amortizationEndDate',     'out': 'amortization_end_date', 'type':'Timestamp'},
    {'in': 'amortizationResidual',    'out': 'amortization_residual', 'type':'String'},
    {'in': 'amortizationSched',       'out': 'amortization_sched', 'type':'RecordRef'},
    {'in': 'amortizStartDate',        'out': 'amortiz_start_date', 'type':'Timestamp'},
    {'in': 'class',                   'out': 'class', 'type':'RecordRef'},
    {'in': 'dueToFromSubsidiary',     'out': 'due_to_from_subsidiary', 'type':'RecordRef'},
    {'in': 'eliminate',               'out': 'eliminate', 'type':'Boolean'},
    {'in': 'endDate',                 'out': 'end_date', 'type':'Timestamp'},
    {'in': 'grossAmt',                'out': 'gross_amt', 'type':'Double'},
    {'in': 'lineFxRate',              'out': 'line_fx_rate', 'type':'Double'},
    {'in': 'lineSubsidiary',          'out': 'line_subsidiary', 'type':'RecordRef'},
    {'in': 'lineTaxCode',             'out': 'line_tax_code', 'type':'RecordRef'},
    {'in': 'lineTaxRate',             'out': 'line_tax_rate', 'type':'Double'},
    {'in': 'lineUnit',                'out': 'line_unit', 'type':'RecordRef'},
    {'in': 'location',                'out': 'location', 'type':'RecordRef'},
    {'in': 'previewDebit',            'out': 'preview_debit', 'type':'String'},
    {'in': 'residual',                'out': 'residual', 'type':'String'},
    {'in': 'revenueRecognitionRule',  'out': 'revenue_recognition_rule', 'type':'RecordRef'},
    {'in': 'schedule',                'out': 'schedule', 'type':'RecordRef'},
    {'in': 'scheduleNum',             'out': 'schedule_num', 'type':'RecordRef'},
    {'in': 'startDate',               'out': 'start_date', 'type':'Timestamp'},
    {'in': 'tax1Acct',                'out': 'tax1_acct', 'type':'RecordRef'},
    {'in': 'tax1Amt',                 'out': 'tax1_amt', 'type':'Double'},
    {'in': 'taxAccount',              'out': 'tax_account', 'type':'RecordRef'},
    {'in': 'taxBasis',                'out': 'tax_basis', 'type':'Double'},
    {'in': 'taxCode',                 'out': 'tax_code', 'type':'RecordRef'},
    {'in': 'taxRate1',                'out': 'tax_rate1', 'type':'Double'},
    {'in': 'totalAmount',             'out': 'total_amount', 'type':'Double'},
    {'in': 'customFieldList',         'out': 'custom_field_list', 'type':'CustomFieldList'},
]
