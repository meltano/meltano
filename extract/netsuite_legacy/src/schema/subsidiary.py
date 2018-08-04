from elt.schema import Schema, Column, DBType

from schema.utils import columns_from_mappings


PG_SCHEMA = 'netsuite'
PG_TABLE = 'subsidiaries'
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
    {'in': 'addrLanguage',            'out': 'addr_language', 'type':'String'},
    {'in': 'allowPayroll',            'out': 'allow_payroll', 'type':'Boolean'},
    {'in': 'checkLayout',             'out': 'check_layout', 'type':'RecordRef'},
    {'in': 'consol',                  'out': 'consol', 'type':'String'},
    {'in': 'country',                 'out': 'country', 'type':'String'},
    {'in': 'currency',                'out': 'currency', 'type':'SubCurrency'},
    {'in': 'edition',                 'out': 'edition', 'type':'String'},
    {'in': 'email',                   'out': 'email', 'type':'String'},
    {'in': 'fax',                     'out': 'fax', 'type':'String'},
    {'in': 'federalIdNumber',         'out': 'federal_id_number', 'type':'String'},
    {'in': 'fiscalCalendar',          'out': 'fiscal_calendar', 'type':'RecordRef'},
    {'in': 'inboundEmail',            'out': 'inbound_email', 'type':'String'},
    {'in': 'interCoAccount',          'out': 'inter_co_account', 'type':'RecordRef'},
    {'in': 'isElimination',           'out': 'is_elimination', 'type':'Boolean'},
    {'in': 'isInactive',              'out': 'is_inactive', 'type':'Boolean'},
    {'in': 'legalName',               'out': 'legal_name', 'type':'String'},
    {'in': 'logo',                    'out': 'logo', 'type':'RecordRef'},
    {'in': 'mainAddress',             'out': 'main_address', 'type':'Address'},
    {'in': 'name',                    'out': 'name', 'type':'String'},
    {'in': 'nonConsol',               'out': 'non_consol', 'type':'String'},
    {'in': 'pageLogo',                'out': 'page_logo', 'type':'RecordRef'},
    {'in': 'parent',                  'out': 'parent', 'type':'RecordRef'},
    {'in': 'purchaseOrderAmount',     'out': 'purchase_order_amount', 'type':'Double'},
    {'in': 'purchaseOrderQuantity',   'out': 'purchase_order_quantity', 'type':'Double'},
    {'in': 'purchaseOrderQuantityDiff', 'out': 'purchase_order_quantity_diff', 'type':'Double'},
    {'in': 'receiptAmount',           'out': 'receipt_amount', 'type':'Double'},
    {'in': 'receiptQuantity',         'out': 'receipt_quantity', 'type':'Double'},
    {'in': 'receiptQuantityDiff',     'out': 'receipt_quantity_diff', 'type':'Double'},
    {'in': 'returnAddress',           'out': 'return_address', 'type':'Address'},
    {'in': 'shippingAddress',         'out': 'shipping_address', 'type':'Address'},
    {'in': 'showSubsidiaryName',      'out': 'show_subsidiary_name', 'type':'Boolean'},
    {'in': 'ssnOrTin',                'out': 'ssn_or_tin', 'type':'String'},
    {'in': 'state',                   'out': 'state', 'type':'String'},
    {'in': 'state1TaxNumber',         'out': 'state1_tax_number', 'type':'String'},
    {'in': 'taxFiscalCalendar',       'out': 'tax_fiscal_calendar', 'type':'RecordRef'},
    {'in': 'tranPrefix',              'out': 'tran_prefix', 'type':'String'},
    {'in': 'url',                     'out': 'url', 'type':'String'},
    {'in': 'customFieldList',         'out': 'custom_field_list', 'type':'CustomFieldList'},
]
