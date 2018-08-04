from elt.schema import Schema, Column, DBType

from schema.utils import columns_from_mappings

PG_SCHEMA = 'netsuite'
PG_TABLE = 'transaction_items'
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
    {'in': 'item',                'out': 'item', 'type':'RecordRef'},
    {'in': 'amount',              'out': 'amount', 'type':'Double'},
    {'in': 'amountOrdered',       'out': 'amount_ordered', 'type':'Double'},
    {'in': 'grossAmt',            'out': 'gross_amt', 'type':'Double'},
    {'in': 'quantity',            'out': 'quantity', 'type':'Double'},
    {'in': 'description',         'out': 'description', 'type':'String'},
    {'in': 'altSalesAmt',         'out': 'alt_sales_amt', 'type':'Double'},
    {'in': 'binNumbers',          'out': 'bin_numbers', 'type':'String'},
    {'in': 'catchUpPeriod',       'out': 'catch_up_period', 'type':'RecordRef'},
    {'in': 'chargesList',         'out': 'charges_list', 'type':'RecordRefList'},
    {'in': 'chargeType',          'out': 'charge_type', 'type':'RecordRef'},
    {'in': 'class',               'out': 'class', 'type':'RecordRef'},
    {'in': 'costEstimate',        'out': 'cost_estimate', 'type':'Double'},
    {'in': 'costEstimateType',    'out': 'cost_estimate_type', 'type':'String'},
    {'in': 'currentPercent',      'out': 'current_percent', 'type':'Double'},
    {'in': 'customer',            'out': 'customer', 'type':'RecordRef'},
    {'in': 'deferRevRec',         'out': 'defer_rev_rec', 'type':'Boolean'},
    {'in': 'department',          'out': 'department', 'type':'RecordRef'},
    {'in': 'excludeFromRateRequest', 'out': 'exclude_from_rate_request', 'type':'Boolean'},
    {'in': 'expandItemGroup',     'out': 'expand_item_group', 'type':'Boolean'},
    {'in': 'expectedShipDate',    'out': 'expected_ship_date', 'type':'Timestamp'},
    {'in': 'expirationDate',      'out': 'expiration_date', 'type':'Timestamp'},
    {'in': 'fromJob',             'out': 'from_job', 'type':'Boolean'},
    {'in': 'giftCertFrom',        'out': 'gift_cert_from', 'type':'String'},
    {'in': 'giftCertMessage',     'out': 'gift_cert_message', 'type':'String'},
    {'in': 'giftCertNumber',      'out': 'gift_cert_number', 'type':'String'},
    {'in': 'giftCertRecipientEmail', 'out': 'gift_cert_recipient_email', 'type':'String'},
    {'in': 'giftCertRecipientName',  'out': 'gift_cert_recipient_name', 'type':'String'},
    {'in': 'isBillable',          'out': 'is_billable', 'type':'Boolean'},
    {'in': 'isEstimate',          'out': 'is_estimate', 'type':'Boolean'},
    {'in': 'isTaxable',           'out': 'is_taxable', 'type':'Boolean'},
    {'in': 'itemIsFulfilled',     'out': 'item_is_fulfilled', 'type':'Boolean'},
    {'in': 'job',                 'out': 'job', 'type':'RecordRef'},
    {'in': 'licenseCode',         'out': 'license_code', 'type':'String'},
    {'in': 'location',            'out': 'location', 'type':'RecordRef'},
    {'in': 'orderLine',           'out': 'order_line', 'type':'Long'},
    {'in': 'percentComplete',     'out': 'percent_complete', 'type':'Double'},
    {'in': 'price',               'out': 'price', 'type':'RecordRef'},
    {'in': 'quantityAvailable',   'out': 'quantity_available', 'type':'Double'},
    {'in': 'quantityFulfilled',   'out': 'quantity_fulfilled', 'type':'Double'},
    {'in': 'quantityOnHand',      'out': 'quantity_on_hand', 'type':'Double'},
    {'in': 'quantityOrdered',     'out': 'quantity_ordered', 'type':'Double'},
    {'in': 'quantityRemaining',   'out': 'quantity_remaining', 'type':'Double'},
    {'in': 'rate',                'out': 'rate', 'type':'String'},
    {'in': 'revRecEndDate',       'out': 'rev_rec_end_date', 'type':'Timestamp'},
    {'in': 'revRecSchedule',      'out': 'rev_rec_schedule', 'type':'RecordRef'},
    {'in': 'revRecStartDate',     'out': 'rev_rec_start_date', 'type':'Timestamp'},
    {'in': 'revRecTermInMonths',  'out': 'rev_rec_term_in_months', 'type':'Long'},
    {'in': 'serialNumbers',       'out': 'serial_numbers', 'type':'String'},
    {'in': 'shipAddress',         'out': 'ship_address', 'type':'RecordRef'},
    {'in': 'shipCarrier',         'out': 'ship_carrier', 'type':'String'},
    {'in': 'shipGroup',           'out': 'ship_group', 'type':'Long'},
    {'in': 'shipMethod',          'out': 'ship_method', 'type':'RecordRef'},
    {'in': 'subscription',        'out': 'subscription', 'type':'RecordRef'},
    {'in': 'subscriptionLine',    'out': 'subscription_line', 'type':'RecordRef'},
    {'in': 'tax1Amt',             'out': 'tax1_amt', 'type':'Double'},
    {'in': 'taxAmount',           'out': 'tax_amount', 'type':'Double'},
    {'in': 'taxCode',             'out': 'tax_code', 'type':'RecordRef'},
    {'in': 'taxDetailsReference', 'out': 'tax_details_reference', 'type':'String'},
    {'in': 'taxRate1',            'out': 'tax_rate1', 'type':'Double'},
    {'in': 'taxRate2',            'out': 'tax_rate2', 'type':'Double'},
    {'in': 'units',               'out': 'units', 'type':'RecordRef'},
    {'in': 'vendorName',          'out': 'vendor_name', 'type':'String'},
    {'in': 'vsoeAllocation',      'out': 'vsoe_allocation', 'type':'Double'},
    {'in': 'vsoeAmount',          'out': 'vsoe_amount', 'type':'Double'},
    {'in': 'vsoeDeferral',        'out': 'vsoe_deferral', 'type':'String'},
    {'in': 'vsoeDelivered',       'out': 'vsoe_delivered', 'type':'Boolean'},
    {'in': 'vsoeIsEstimate',      'out': 'vsoe_is_estimate', 'type':'Boolean'},
    {'in': 'vsoePermitDiscount',  'out': 'vsoe_permit_discount', 'type':'String'},
    {'in': 'vsoePrice',           'out': 'vsoe_price', 'type':'Double'},
    {'in': 'vsoeSopGroup',        'out': 'vsoe_sop_group', 'type':'String'},
    {'in': 'amortizationEndDate', 'out': 'amortization_end_date', 'type':'Timestamp'},
    {'in': 'amortizationResidual', 'out': 'amortization_residual', 'type':'String'},
    {'in': 'amortizationSched',   'out': 'amortization_sched', 'type':'RecordRef'},
    {'in': 'amortizStartDate',    'out': 'amortiz_start_date', 'type':'Timestamp'},
    {'in': 'billreceiptsList',    'out': 'billreceipts_list', 'type':'RecordRefList'},
    {'in': 'billVarianceStatus',  'out': 'bill_variance_status', 'type':'String'},
    {'in': 'landedCostCategory',  'out': 'landed_cost_category', 'type':'RecordRef'},
    {'in': 'orderDoc',            'out': 'order_doc', 'type':'Long'},

    # PurchaseOrderItem
    {'in': 'createdFrom',         'out': 'created_from', 'type':'RecordRef'},
    {'in': 'expectedReceiptDate', 'out': 'expected_receipt_date', 'type':'Timestamp'},
    {'in': 'isClosed',            'out': 'is_closed', 'type':'Boolean'},
    {'in': 'linkedOrderList',     'out': 'linked_order_list', 'type':'RecordRefList'},
    {'in': 'matchBillToReceipt',  'out': 'match_bill_to_receipt', 'type':'Boolean'},
    {'in': 'purchaseContract',    'out': 'purchase_contract', 'type':'RecordRef'},
    {'in': 'quantityBilled',      'out': 'quantity_billed', 'type':'Double'},
    {'in': 'quantityOnShipments', 'out': 'quantity_on_shipments', 'type':'Double'},
    {'in': 'quantityReceived',    'out': 'quantity_received', 'type':'Double'},

    {'in': 'options',             'out': 'options', 'type':'CustomFieldList'},
    {'in': 'customFieldList',     'out': 'custom_field_list', 'type':'CustomFieldList'},
]
