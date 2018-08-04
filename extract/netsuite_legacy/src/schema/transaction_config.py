# A list of all available transaction types
TRANSACTION_TYPES = [
                      '_assemblyBuild',
                      '_assemblyUnbuild',
                      '_binTransfer',
                      '_binWorksheet',
                      '_cashRefund',
                      '_cashSale',
                      '_check',
                      '_creditMemo',
                      '_custom',
                      '_customerDeposit',
                      '_customerPayment',
                      '_customerRefund',
                      '_deposit',
                      '_depositApplication',
                      '_estimate',
                      '_expenseReport',
                      '_inboundShipment',
                      '_inventoryAdjustment',
                      '_inventoryCostRevaluation',
                      '_inventoryTransfer',
                      '_invoice',
                      '_itemFulfillment',
                      '_itemReceipt',
                      '_journal',
                      '_opportunity',
                      '_paycheck',
                      '_paycheckJournal',
                      '_purchaseOrder',
                      '_requisition',
                      '_returnAuthorization',
                      '_salesOrder',
                      '_transferOrder',
                      '_vendorBill',
                      '_vendorCredit',
                      '_vendorPayment',
                      '_vendorReturnAuthorization',
                      '_workOrder',
                      '_workOrderClose',
                      '_workOrderCompletion',
                      '_workOrderIssue',
                  ]


# Column Mappings for Transactions used in order to:
# (1) Automatically generate the schema
# (2) Transform the data exported from the API endpoints to the schema we use
#     for storing the result of the ELT process
#
# in: The name of the attribute as provided by the API
# out: A template for the name of the exported attribute(s).
#      Can be the same in case of simple types (String, Boolean, etc) that result in one attribute
#       or result in multiple output attributes (e.g. in case of an address)
# type: The data type. Either a simple type (Integer, Long, Float, etc) or
#        anything other specific to this ELT.
#       For example in NetSuite ELT we have: RecordRef (we only keep id and name)
#        and Address (results in 12 output attributes)
COLUMN_MAPPINGS = [
    {'in': 'externalId',            'out': 'external_id', 'type':'String'},
    {'in': 'createdDate',           'out': 'created_date', 'type':'Timestamp'},
    {'in': 'lastModifiedDate',      'out': 'last_modified_date', 'type':'Timestamp'},
    {'in': 'nexus',                 'out': 'nexus', 'type':'RecordRef'},
    {'in': 'subsidiaryTaxRegNum',   'out': 'subsidiary_tax_reg_num', 'type':'RecordRef'},
    {'in': 'tranDate',              'out': 'tran_date', 'type':'Timestamp'},
    {'in': 'tranId',                'out': 'tran_id', 'type':'String'},
    {'in': 'userTotal',             'out': 'user_total', 'type':'Double'},
    {'in': 'paymentHold',           'out': 'payment_hold', 'type':'Boolean'},
    {'in': 'creditLimit',           'out': 'credit_limit', 'type':'Double'},
    {'in': 'availableVendorCredit', 'out': 'available_vendor_credit', 'type':'Double'},
    {'in': 'landedCostMethod',      'out': 'landed_cost_method', 'type':'String'},
    {'in': 'landedCostPerLine',     'out': 'landed_cost_per_line', 'type':'Boolean'},
    {'in': 'transactionNumber',     'out': 'transaction_number', 'type':'String'},
    {'in': 'address',               'out': 'address', 'type':'String'},
    {'in': 'billPay',               'out': 'bill_pay', 'type':'Boolean'},
    {'in': 'taxRegOverride',        'out': 'tax_reg_override', 'type':'Boolean'},
    {'in': 'taxDetailsOverride',    'out': 'tax_details_override', 'type':'Boolean'},
    {'in': 'customForm',            'out': 'custom_form', 'type':'RecordRef'},
    {'in': 'nextApprover',          'out': 'next_approver', 'type':'RecordRef'},
    {'in': 'entity',                'out': 'entity', 'type':'RecordRef'},
    {'in': 'billingAccount',        'out': 'billing_account', 'type':'RecordRef'},
    {'in': 'recurringBill',         'out': 'recurring_bill', 'type':'Boolean'},
    {'in': 'entityTaxRegNum',       'out': 'entity_tax_reg_num', 'type':'RecordRef'},
    {'in': 'source',                'out': 'source', 'type':'String'},
    {'in': 'createdFrom',           'out': 'created_from', 'type':'RecordRef'},
    {'in': 'postingPeriod',         'out': 'posting_period', 'type':'RecordRef'},
    {'in': 'opportunity',           'out': 'opportunity', 'type':'RecordRef'},
    {'in': 'department',            'out': 'department', 'type':'RecordRef'},
    {'in': 'class',                 'out': 'class', 'type':'RecordRef'},
    {'in': 'terms',                 'out': 'terms', 'type':'RecordRef'},
    {'in': 'location',              'out': 'location', 'type':'RecordRef'},
    {'in': 'subsidiary',            'out': 'subsidiary', 'type':'RecordRef'},
    {'in': 'currency',              'out': 'currency_ref', 'type':'RecordRef'},
    {'in': 'dueDate',               'out': 'due_date', 'type':'Timestamp'},
    {'in': 'discountDate',          'out': 'discount_date', 'type':'Timestamp'},
    {'in': 'discountAmount',        'out': 'discount_amount', 'type':'Double'},
    {'in': 'salesRep',              'out': 'sales_rep', 'type':'RecordRef'},
    {'in': 'contribPct',            'out': 'contrib_pct', 'type':'String'},
    {'in': 'partner',               'out': 'partner', 'type':'RecordRef'},
    {'in': 'leadSource',            'out': 'lead_source', 'type':'RecordRef'},
    {'in': 'startDate',             'out': 'start_date', 'type':'Timestamp'},
    {'in': 'endDate',               'out': 'end_date', 'type':'Timestamp'},
    {'in': 'otherRefNum',           'out': 'other_ref_num', 'type':'String'},
    {'in': 'memo',                  'out': 'memo', 'type':'String'},
    {'in': 'salesEffectiveDate',    'out': 'sales_effective_date', 'type':'Timestamp'},
    {'in': 'excludeCommission',     'out': 'exclude_commission', 'type':'Boolean'},
    {'in': 'totalCostEstimate',     'out': 'total_cost_estimate', 'type':'Double'},
    {'in': 'estGrossProfit',        'out': 'est_gross_profit', 'type':'Double'},
    {'in': 'estGrossProfitPercent', 'out': 'est_gross_profit_percent', 'type':'Double'},
    {'in': 'revRecSchedule',        'out': 'rev_rec_schedule', 'type':'RecordRef'},
    {'in': 'revRecStartDate',       'out': 'rev_rec_start_date', 'type':'Timestamp'},
    {'in': 'revRecEndDate',         'out': 'rev_rec_end_date', 'type':'Timestamp'},
    {'in': 'amountPaid',            'out': 'amount_paid', 'type':'Double'},
    {'in': 'amountRemaining',       'out': 'amount_remaining', 'type':'Double'},
    {'in': 'balance',               'out': 'balance', 'type':'Double'},
    {'in': 'account',               'out': 'account', 'type':'RecordRef'},
    {'in': 'onCreditHold',          'out': 'on_credit_hold', 'type':'String'},
    {'in': 'exchangeRate',          'out': 'exchange_rate', 'type':'Double'},
    {'in': 'currencyName',          'out': 'currency_name', 'type':'String'},
    {'in': 'promoCode',             'out': 'promo_code', 'type':'RecordRef'},
    {'in': 'discountItem',          'out': 'discount_item', 'type':'RecordRef'},
    {'in': 'discountRate',          'out': 'discount_rate', 'type':'String'},
    {'in': 'isTaxable',             'out': 'is_taxable', 'type':'Boolean'},
    {'in': 'taxItem',               'out': 'tax_item', 'type':'RecordRef'},
    {'in': 'taxRate',               'out': 'tax_rate', 'type':'Double'},
    {'in': 'toBePrinted',           'out': 'to_be_printed', 'type':'Boolean'},
    {'in': 'toBeEmailed',           'out': 'to_be_emailed', 'type':'Boolean'},
    {'in': 'toBeFaxed',             'out': 'to_be_faxed', 'type':'Boolean'},
    {'in': 'fax',                   'out': 'fax', 'type':'String'},
    {'in': 'messageSel',            'out': 'message_sel', 'type':'RecordRef'},
    {'in': 'message',               'out': 'message', 'type':'String'},
    {'in': 'billingAddress',        'out': 'billing_address', 'type':'Address'},
    {'in': 'billAddressList',       'out': 'bill_address_list', 'type':'RecordRef'},
    {'in': 'shippingAddress',       'out': 'shipping_address', 'type':'Address'},
    {'in': 'shipAddressList',       'out': 'ship_address_list', 'type':'RecordRef'},
    {'in': 'shipIsResidential',     'out': 'ship_is_residential', 'type':'Boolean'},
    {'in': 'fob',                   'out': 'fob', 'type':'String'},
    {'in': 'shipDate',              'out': 'ship_date', 'type':'Timestamp'},
    {'in': 'shipMethod',            'out': 'ship_method', 'type':'RecordRef'},
    {'in': 'shippingCost',          'out': 'shipping_cost', 'type':'Double'},
    {'in': 'shippingTax1Rate',      'out': 'shipping_tax1_rate', 'type':'Double'},
    {'in': 'shippingTax2Rate',      'out': 'shipping_tax2_rate', 'type':'String'},
    {'in': 'shippingTaxCode',       'out': 'shipping_tax_code', 'type':'RecordRef'},
    {'in': 'handlingTaxCode',       'out': 'handling_tax_code', 'type':'RecordRef'},
    {'in': 'handlingTax1Rate',      'out': 'handling_tax1_rate', 'type':'Double'},
    {'in': 'handlingCost',          'out': 'handling_cost', 'type':'Double'},
    {'in': 'handlingTax2Rate',      'out': 'handling_tax2_rate', 'type':'String'},
    {'in': 'trackingNumbers',       'out': 'tracking_numbers', 'type':'String'},
    {'in': 'linkedTrackingNumbers', 'out': 'linked_tracking_numbers', 'type':'String'},
    {'in': 'salesGroup',            'out': 'sales_group', 'type':'RecordRef'},
    {'in': 'subTotal',              'out': 'sub_total', 'type':'Double'},
    {'in': 'canHaveStackable',      'out': 'can_have_stackable', 'type':'Boolean'},
    {'in': 'revenueStatus',         'out': 'revenue_status', 'type':'String'},
    {'in': 'recognizedRevenue',     'out': 'recognized_revenue', 'type':'Double'},
    {'in': 'deferredRevenue',       'out': 'deferred_revenue', 'type':'Double'},
    {'in': 'revRecOnRevCommitment', 'out': 'rev_rec_on_rev_commitment', 'type':'Boolean'},
    {'in': 'syncSalesTeams',        'out': 'sync_sales_teams', 'type':'Boolean'},
    {'in': 'discountTotal',         'out': 'discount_total', 'type':'Double'},
    {'in': 'taxTotal',              'out': 'tax_total', 'type':'Double'},
    {'in': 'altShippingCost',       'out': 'alt_shipping_cost', 'type':'Double'},
    {'in': 'altHandlingCost',       'out': 'alt_handling_cost', 'type':'Double'},
    {'in': 'total',                 'out': 'total', 'type':'Double'},
    {'in': 'status',                'out': 'status', 'type':'String'},
    {'in': 'job',                   'out': 'job', 'type':'RecordRef'},
    {'in': 'billingSchedule',       'out': 'billing_schedule', 'type':'RecordRef'},
    {'in': 'email',                 'out': 'email', 'type':'String'},
    {'in': 'tax2Total',             'out': 'tax2_total', 'type':'Double'},
    {'in': 'vatRegNum',             'out': 'vat_reg_num', 'type':'String'},
    {'in': 'expCostDiscount',       'out': 'exp_cost_discount', 'type':'RecordRef'},
    {'in': 'itemCostDiscount',      'out': 'item_cost_discount', 'type':'RecordRef'},
    {'in': 'timeDiscount',          'out': 'time_discount', 'type':'RecordRef'},
    {'in': 'expCostDiscRate',       'out': 'exp_cost_disc_rate', 'type':'String'},
    {'in': 'itemCostDiscRate',      'out': 'item_cost_disc_rate', 'type':'String'},
    {'in': 'timeDiscRate',          'out': 'time_disc_rate', 'type':'String'},
    {'in': 'expCostDiscAmount',     'out': 'exp_cost_disc_amount', 'type':'Double'},
    {'in': 'expCostTaxRate1',       'out': 'exp_cost_tax_rate1', 'type':'Double'},
    {'in': 'expCostTaxRate2',       'out': 'exp_cost_tax_rate2', 'type':'Double'},
    {'in': 'itemCostDiscAmount',    'out': 'item_cost_disc_amount', 'type':'Double'},
    {'in': 'expCostTaxCode',        'out': 'exp_cost_tax_code', 'type':'RecordRef'},
    {'in': 'expCostDiscTax1Amt',    'out': 'exp_cost_disc_tax1_amt', 'type':'Double'},
    {'in': 'itemCostTaxRate1',      'out': 'item_cost_tax_rate1', 'type':'Double'},
    {'in': 'timeDiscAmount',        'out': 'time_disc_amount', 'type':'Double'},
    {'in': 'itemCostTaxCode',       'out': 'item_cost_tax_code', 'type':'RecordRef'},
    {'in': 'expCostDiscTaxable',    'out': 'exp_cost_disc_taxable', 'type':'Boolean'},
    {'in': 'itemCostDiscTaxable',   'out': 'item_cost_disc_taxable', 'type':'Boolean'},
    {'in': 'itemCostTaxRate2',      'out': 'item_cost_tax_rate2', 'type':'Double'},
    {'in': 'itemCostDiscTax1Amt',   'out': 'item_cost_disc_tax1_amt', 'type':'Double'},
    {'in': 'itemCostDiscPrint',     'out': 'item_cost_disc_print', 'type':'Boolean'},
    {'in': 'timeDiscTaxable',       'out': 'time_disc_taxable', 'type':'Boolean'},
    {'in': 'timeTaxRate1',          'out': 'time_tax_rate1', 'type':'Double'},
    {'in': 'expCostDiscPrint',      'out': 'exp_cost_disc_print', 'type':'Boolean'},
    {'in': 'timeTaxCode',           'out': 'time_tax_code', 'type':'RecordRef'},
    {'in': 'timeDiscPrint',         'out': 'time_disc_print', 'type':'Boolean'},
    {'in': 'timeDiscTax1Amt',       'out': 'time_disc_tax1_amt', 'type':'Double'},
    {'in': 'tranIsVsoeBundle',      'out': 'tran_is_vsoe_bundle', 'type':'Boolean'},
    {'in': 'timeTaxRate2',          'out': 'time_tax_rate2', 'type':'Double'},
    {'in': 'vsoeAutoCalc',          'out': 'vsoe_auto_calc', 'type':'Boolean'},
    {'in': 'syncPartnerTeams',      'out': 'sync_partner_teams', 'type':'Boolean'},
    {'in': 'approvalStatus',        'out': 'approval_status', 'type':'RecordRef'},

    # AdvInterCompanyJournalEntry
    {'in': 'accountingBook',        'out': 'accounting_book', 'type':'RecordRef'},
    {'in': 'accountingBookDetailList', 'out': 'accounting_book_detail_list', 'type':'ENTITY_LIST_AS_JSON'},
    {'in': 'approved',              'out': 'approved', 'type':'Boolean'},
    {'in': 'isBookSpecific',        'out': 'is_book_specific', 'type':'Boolean'},
    {'in': 'parentExpenseAlloc',    'out': 'parent_expense_alloc', 'type':'RecordRef'},
    {'in': 'performAutoBalance',    'out': 'perform_auto_balance', 'type':'Boolean'},
    {'in': 'reversalDate',          'out': 'reversal_date', 'type':'Timestamp'},
    {'in': 'reversalDefer',         'out': 'reversal_defer', 'type':'Boolean'},
    {'in': 'reversalEntry',         'out': 'reversal_entry', 'type':'String'},

    # InterCompanyJournalEntry
    {'in': 'toSubsidiary',          'out': 'to_subsidiary', 'type':'RecordRef'},

    # StatisticalJournalEntry
    {'in': 'unitsType',             'out': 'units_type', 'type':'RecordRef'},

    # Check
    {'in': 'voidJournal',           'out': 'void_journal', 'type':'RecordRef'},
    {'in': 'landedCostsList',       'out': 'landed_costs_list', 'type':'ENTITY_LIST_AS_JSON'},

    # Credit Memo
    {'in': 'applied',               'out': 'applied', 'type':'Double'},
    {'in': 'autoApply',             'out': 'auto_apply', 'type':'Boolean'},
    {'in': 'giftCert',              'out': 'gift_cert', 'type':'RecordRef'},
    {'in': 'giftCertApplied',       'out': 'gift_cert_applied', 'type':'Double'},
    {'in': 'giftCertAvailable',     'out': 'gift_cert_available', 'type':'Double'},
    {'in': 'giftCertTotal',         'out': 'gift_cert_total', 'type':'Double'},
    {'in': 'isMultiShipTo',         'out': 'is_multi_ship_to', 'type':'Boolean'},
    {'in': 'partnersList',          'out': 'partners_list', 'type':'ENTITY_LIST_AS_JSON'},
    {'in': 'salesTeamList',         'out': 'sales_team_list', 'type':'ENTITY_LIST_AS_JSON'},
    {'in': 'taxDetailsList',        'out': 'tax_details_list', 'type':'ENTITY_LIST_AS_JSON'},
    {'in': 'unapplied',             'out': 'unapplied', 'type':'Double'},

    # Customer Deposit / Refund / Payment
    {'in': 'arAcct',                'out': 'ar_acct', 'type':'RecordRef'},
    {'in': 'customer',              'out': 'customer', 'type':'RecordRef'},
    {'in': 'depositList',           'out': 'deposit_list', 'type':'ENTITY_LIST_AS_JSON'},
    {'in': 'isRecurringPayment',    'out': 'is_recurring_payment', 'type':'Boolean'},
    {'in': 'payment',               'out': 'payment', 'type':'Double'},
    {'in': 'paymentMethod',         'out': 'payment_method', 'type':'RecordRef'},
    {'in': 'salesOrder',            'out': 'sales_order', 'type':'RecordRef'},
    {'in': 'softDescriptor',        'out': 'soft_descriptor', 'type':'String'},
    # Skipping all the creditCard info as they are super sensitive PII
    # ccApproved, ccExpireDate, ccName, ccNumber, creditCard, debitCardIssueNo, etc ..

    # Deposit
    {'in': 'cashBackList',          'out': 'cash_back_list', 'type':'ENTITY_LIST_AS_JSON'},
    {'in': 'otherList',             'out': 'other_list', 'type':'ENTITY_LIST_AS_JSON'},
    {'in': 'paymentList',           'out': 'payment_list', 'type':'ENTITY_LIST_AS_JSON'},

    # DepositApplication
    {'in': 'depDate',               'out': 'dep_date', 'type':'Timestamp'},
    {'in': 'deposit',               'out': 'deposit', 'type':'RecordRef'},

    # Estimate
    {'in': 'altSalesTotal',         'out': 'alt_sales_total', 'type':'Double'},
    {'in': 'entityStatus',          'out': 'entity_status', 'type':'RecordRef'},
    {'in': 'expectedCloseDate',     'out': 'expected_close_date', 'type':'Timestamp'},
    {'in': 'forecastType',          'out': 'forecast_type', 'type':'RecordRef'},
    {'in': 'includeInForecast',     'out': 'include_in_forecast', 'type':'Boolean'},
    {'in': 'oneTime',               'out': 'one_time', 'type':'Double'},
    {'in': 'probability',           'out': 'probability', 'type':'Double'},
    {'in': 'recurAnnually',         'out': 'recur_annually', 'type':'Double'},
    {'in': 'recurMonthly',          'out': 'recur_monthly', 'type':'Double'},
    {'in': 'recurQuarterly',        'out': 'recur_quarterly', 'type':'Double'},
    {'in': 'recurWeekly',           'out': 'recur_qeekly', 'type':'Double'},
    {'in': 'title',                 'out': 'title', 'type':'String'},
    {'in': 'visibleToCustomer',     'out': 'visible_to_customer', 'type':'Boolean'},

    # ExpenseReport
    {'in': 'accountingApproval',    'out': 'accounting_approval', 'type':'Boolean'},
    {'in': 'advance',               'out': 'advance', 'type':'Double'},
    {'in': 'amount',                'out': 'amount', 'type':'Double'},
    {'in': 'complete',              'out': 'complete', 'type':'Boolean'},
    {'in': 'supervisorApproval',    'out': 'supervisor_approval', 'type':'Boolean'},
    {'in': 'tax1Amt',               'out': 'tax1_amt', 'type':'Double'},
    {'in': 'tax2Amt',               'out': 'tax2_amt', 'type':'Double'},
    {'in': 'useMultiCurrency',      'out': 'use_multi_currency', 'type':'Boolean'},

    # InterCompanyTransferOrder
    {'in': 'employee',              'out': 'employee', 'type':'RecordRef'},
    {'in': 'incoterm',              'out': 'incoterm', 'type':'RecordRef'},
    {'in': 'orderStatus',           'out': 'order_status', 'type':'String'},
    {'in': 'shipComplete',          'out': 'ship_complete', 'type':'Boolean'},
    {'in': 'transferLocation',      'out': 'transfer_location', 'type':'RecordRef'},
    {'in': 'useItemCostAsTransferCost', 'out': 'use_item_cost_as_transfer_cost', 'type':'Boolean'},

    # Invoice
    {'in': 'expCostList',           'out': 'exp_cost_list', 'type':'ENTITY_LIST_AS_JSON'},
    {'in': 'giftCertRedemptionList', 'out': 'gift_cert_redemption_list', 'type':'ENTITY_LIST_AS_JSON'},
    {'in': 'itemCostList',          'out': 'item_cost_list', 'type':'ENTITY_LIST_AS_JSON'},
    {'in': 'promotionsList',        'out': 'promotions_list', 'type':'ENTITY_LIST_AS_JSON'},
    {'in': 'shipGroupList',         'out': 'ship_group_list', 'type':'ENTITY_LIST_AS_JSON'},
    {'in': 'timeList',              'out': 'time_list', 'type':'ENTITY_LIST_AS_JSON'},

    # PurchaseOrder
    {'in': 'purchaseContract',      'out': 'purchase_contract', 'type':'RecordRef'},
    {'in': 'shipTo',                'out': 'ship_to', 'type':'RecordRef'},

    # ReturnAuthorization
    {'in': 'revCommitStatus',       'out': 'rev_commit_status', 'type':'String'},
    {'in': 'shipAddress',           'out': 'ship_address', 'type':'String'},

    # VendorBill
    {'in': 'purchaseOrderList',     'out': 'purchase_order_list', 'type':'RecordRefList'},

    # VendorCredit
    {'in': 'unApplied',             'out': 'un_applied', 'type':'Double'},
    {'in': 'userTaxTotal',          'out': 'user_tax_total', 'type':'Double'},

    # VendorPayment
    {'in': 'apAcct',                'out': 'ap_acct', 'type':'RecordRef'},
    {'in': 'creditList',            'out': 'credit_list', 'type':'ENTITY_LIST_AS_JSON'},
    {'in': 'printVoucher',          'out': 'print_voucher', 'type':'Boolean'},
    {'in': 'toAch',                 'out': 'to_ach', 'type':'Boolean'},

    # VendorReturnAuthorization
    {'in': 'intercoStatus',         'out': 'interco_status', 'type':'String'},
    {'in': 'intercoTransaction',    'out': 'interco_transaction', 'type':'RecordRef'},

    # Entity Lists
    {'in': 'applyList',             'out': 'apply_list', 'type':'ENTITY_LIST'},
    {'in': 'lineList',              'out': 'line_list', 'type':'ENTITY_LIST'},
    {'in': 'itemList',              'out': 'item_list', 'type':'ENTITY_LIST'},
    {'in': 'expenseList',           'out': 'expense_list', 'type':'ENTITY_LIST'},

    {'in': 'customFieldList',       'out': 'custom_field_list', 'type':'CustomFieldList'},
]


# The related entities provided as sub-structures when fetching Transactions
# The entries in this dictionary refer to columns in COLUMN_MAPPINGS with 'type':'ENTITY_LIST_AS_JSON'
# While importing a transaction, they are used in order to identify the schema of
#  the related entries and create a record for each one.
#
# Be careful not to add cyclical references (be careful with ENTITY_LIST_AS_JSON inside RELATED_ENTITIES)
#  (ENTITY_LIST 1 --> ENTITY_LIST 2 --> ENTITY_LIST 1)
# as it will result in endless loops while automatically fetching records (fetch_attribute)
#
# In 'node_names', we store all the valid node names for each Entity in order to
#  group together very similar entities. e.g. the almost identical accountingBookDetail
#  in Check, CreditMemo, Deposit, Invoice, etc and
#  the pretty similar interCompanyJournalEntryAccountingBookDetail from Journal entries
RELATED_ENTITIES = {
    'itemList': {
        'class_name': 'TransactionItem',
        'node_names': ['item'],
    },

    'lineList': {
        'class_name': 'TransactionLine',
        'node_names': ['line', 'statisticalJournalEntryLine'],
    },

    'expenseList': {
        'class_name': 'Expense',
        'node_names': ['expense'],
    },

    'accountingBookDetailList': {
        'node_names': ['accountingBookDetail', 'interCompanyJournalEntryAccountingBookDetail'],
        'column_map': [
            {'in': 'accountingBook',      'out': 'accountingBook', 'type':'RecordRef'},
            {'in': 'currency',            'out': 'currency', 'type':'RecordRef'},
            {'in': 'exchangeRate',        'out': 'exchangeRate', 'type':'Double'},
            {'in': 'subsidiary',          'out': 'subsidiary', 'type':'RecordRef'},
        ],
    },

    'applyList': {
        'class_name': 'Application',
        'node_names': ['apply'],
    },

    'partnersList': {
        'node_names': ['partners'],
        'column_map': [
            {'in': 'contribution',        'out': 'contribution', 'type':'Double'},
            {'in': 'isPrimary',           'out': 'isPrimary', 'type':'Boolean'},
            {'in': 'partner',             'out': 'partner', 'type':'RecordRef'},
            {'in': 'partnerRole',         'out': 'partnerRole', 'type':'RecordRef'},
        ],
    },

    'salesTeamList': {
        'node_names': ['salesTeam'],
        'column_map': [
            {'in': 'contribution',        'out': 'contribution', 'type':'Double'},
            {'in': 'employee',            'out': 'employee', 'type':'RecordRef'},
            {'in': 'isPrimary',           'out': 'isPrimary', 'type':'Boolean'},
            {'in': 'salesRole',           'out': 'salesRole', 'type':'RecordRef'},
        ],
    },

    'taxDetailsList': {
        'node_names': ['taxDetails'],
        'column_map': [
            {'in': 'calcDetail',          'out': 'calcDetail', 'type':'String'},
            {'in': 'grossAmount',         'out': 'grossAmount', 'type':'Double'},
            {'in': 'netAmount',           'out': 'netAmount', 'type':'Double'},
            {'in': 'taxAmount',           'out': 'taxAmount', 'type':'Double'},
            {'in': 'taxBasis',            'out': 'taxBasis', 'type':'Double'},
            {'in': 'taxCode',             'out': 'taxCode', 'type':'RecordRef'},
            {'in': 'taxDetailsReference', 'out': 'taxDetailsReference', 'type':'String'},
            {'in': 'taxRate',             'out': 'taxRate', 'type':'Double'},
            {'in': 'taxType',             'out': 'taxType', 'type':'RecordRef'},
        ],
    },

    'landedCostsList': {
        'node_names': ['landedCost'],
        'column_map': [
            {'in': 'amount',              'out': 'amount', 'type':'Double'},
            {'in': 'category',            'out': 'category', 'type':'RecordRef'},
            {'in': 'source',              'out': 'source', 'type':'String'},
            {'in': 'transaction',         'out': 'transaction', 'type':'RecordRef'},
        ],
    },

    'depositList': {
        'node_names': ['customerRefundDeposit'],
        'column_map': [
            {'in': 'amount',              'out': 'amount', 'type':'Double'},
            {'in': 'apply',               'out': 'apply', 'type':'Boolean'},
            {'in': 'currency',            'out': 'currency', 'type':'String'},
            {'in': 'depositDate',         'out': 'depositDate', 'type':'Timestamp'},
            {'in': 'doc',                 'out': 'doc', 'type':'Long'},
            {'in': 'line',                'out': 'line', 'type':'Long'},
            {'in': 'refNum',              'out': 'refNum', 'type':'String'},
            {'in': 'remaining',           'out': 'remaining', 'type':'Double'},
            {'in': 'total',               'out': 'total', 'type':'Double'},
        ],
    },

    'cashBackList': {
        'node_names': ['depositCashBack'],
        'column_map': [
            {'in': 'account',             'out': 'account', 'type':'RecordRef'},
            {'in': 'amount',              'out': 'amount', 'type':'Double'},
            {'in': 'class',               'out': 'class', 'type':'RecordRef'},
            {'in': 'department',          'out': 'department', 'type':'RecordRef'},
            {'in': 'location',            'out': 'location', 'type':'RecordRef'},
            {'in': 'memo',                'out': 'memo', 'type':'String'},
        ],
    },

    'otherList': {
        'node_names': ['depositOther'],
        'column_map': [
            {'in': 'account',             'out': 'account', 'type':'RecordRef'},
            {'in': 'amount',              'out': 'amount', 'type':'Double'},
            {'in': 'class',               'out': 'class', 'type':'RecordRef'},
            {'in': 'department',          'out': 'department', 'type':'RecordRef'},
            {'in': 'entity',              'out': 'entity', 'type':'RecordRef'},
            {'in': 'location',            'out': 'location', 'type':'RecordRef'},
            {'in': 'memo',                'out': 'memo', 'type':'String'},
            {'in': 'paymentMethod',       'out': 'paymentMethod', 'type':'RecordRef'},
            {'in': 'refNum',              'out': 'refNum', 'type':'String'},
        ],
    },

    'paymentList': {
        'node_names': ['depositPayment'],
        'column_map': [
            {'in': 'currency',            'out': 'currency', 'type':'RecordRef'},
            {'in': 'deposit',             'out': 'deposit', 'type':'Boolean'},
            {'in': 'docDate',             'out': 'docDate', 'type':'Timestamp'},
            {'in': 'docNumber',           'out': 'docNumber', 'type':'String'},
            {'in': 'entity',              'out': 'entity', 'type':'RecordRef'},
            {'in': 'id',                  'out': 'id', 'type':'Long'},
            {'in': 'lineId',              'out': 'lineId', 'type':'Long'},
            {'in': 'memo',                'out': 'memo', 'type':'String'},
            {'in': 'paymentAmount',       'out': 'paymentAmount', 'type':'Double'},
            {'in': 'paymentMethod',       'out': 'paymentMethod', 'type':'RecordRef'},
            {'in': 'refNum',              'out': 'refNum', 'type':'String'},
            {'in': 'transactionAmount',   'out': 'transactionAmount', 'type':'Double'},
            {'in': 'type',                'out': 'type', 'type':'String'},
        ],
    },

    'expCostList': {
        'node_names': ['expCost'],
        'column_map': [
            {'in': 'amount',              'out': 'amount', 'type':'Double'},
            {'in': 'apply',               'out': 'apply', 'type':'Boolean'},
            {'in': 'billedDate',          'out': 'billedDate', 'type':'Timestamp'},
            {'in': 'categoryDisp',        'out': 'categoryDisp', 'type':'String'},
            {'in': 'class',               'out': 'class', 'type':'String'},
            {'in': 'department',          'out': 'department', 'type':'String'},
            {'in': 'doc',                 'out': 'doc', 'type':'Long'},
            {'in': 'employeeDisp',        'out': 'employeeDisp', 'type':'String'},
            {'in': 'grossAmt',            'out': 'grossAmt', 'type':'Double'},
            {'in': 'jobDisp',             'out': 'jobDisp', 'type':'String'},
            {'in': 'line',                'out': 'line', 'type':'Long'},
            {'in': 'location',            'out': 'location', 'type':'String'},
            {'in': 'memo',                'out': 'memo', 'type':'String'},
            {'in': 'originalAmount',      'out': 'originalAmount', 'type':'Double'},
            {'in': 'revRecEndDate',       'out': 'revRecEndDate', 'type':'Timestamp'},
            {'in': 'revRecSchedule',      'out': 'revRecSchedule', 'type':'RecordRef'},
            {'in': 'revRecStartDate',     'out': 'revRecStartDate', 'type':'Timestamp'},
            {'in': 'tax1Amt',             'out': 'tax1Amt', 'type':'Double'},
            {'in': 'taxableDisp',         'out': 'taxableDisp', 'type':'String'},
            {'in': 'taxAmount',           'out': 'taxAmount', 'type':'Double'},
            {'in': 'taxCode',             'out': 'taxCode', 'type':'RecordRef'},
            {'in': 'taxDetailsReference', 'out': 'taxDetailsReference', 'type':'String'},
            {'in': 'taxRate1',            'out': 'taxRate1', 'type':'Double'},
            {'in': 'taxRate2',            'out': 'taxRate2', 'type':'Double'},
        ],
    },

    'giftCertRedemptionList': {
        'node_names': ['giftCertRedemption'],
        'column_map': [
            {'in': 'authCode',            'out': 'authCode', 'type':'RecordRef'},
            {'in': 'authCodeAmtRemaining', 'out': 'authCodeAmtRemaining', 'type':'Double'},
            {'in': 'authCodeApplied',     'out': 'authCodeApplied', 'type':'Double'},
            {'in': 'giftCertAvailable',   'out': 'giftCertAvailable', 'type':'Double'},
        ],
    },

    'itemCostList': {
        'node_names': ['itemCost'],
        'column_map': [
            {'in': 'amount',              'out': 'amount', 'type':'Double'},
            {'in': 'apply',               'out': 'apply', 'type':'Boolean'},
            {'in': 'billedDate',          'out': 'billedDate', 'type':'Timestamp'},
            {'in': 'class',               'out': 'class', 'type':'String'},
            {'in': 'cost',                'out': 'cost', 'type':'Double'},
            {'in': 'department',          'out': 'department', 'type':'String'},
            {'in': 'doc',                 'out': 'doc', 'type':'Long'},
            {'in': 'grossAmt',            'out': 'grossAmt', 'type':'Double'},
            {'in': 'itemCostCount',       'out': 'itemCostCount', 'type':'String'},
            {'in': 'itemDisp',            'out': 'itemDisp', 'type':'String'},
            {'in': 'jobDisp',             'out': 'jobDisp', 'type':'String'},
            {'in': 'line',                'out': 'line', 'type':'Long'},
            {'in': 'location',            'out': 'location', 'type':'String'},
            {'in': 'memo',                'out': 'memo', 'type':'String'},
            {'in': 'quantity',            'out': 'quantity', 'type':'String'},
            {'in': 'revRecEndDate',       'out': 'revRecEndDate', 'type':'Timestamp'},
            {'in': 'revRecSchedule',      'out': 'revRecSchedule', 'type':'RecordRef'},
            {'in': 'revRecStartDate',     'out': 'revRecStartDate', 'type':'Timestamp'},
            {'in': 'serialNumbers',       'out': 'serialNumbers', 'type':'String'},
            {'in': 'tax1Amt',             'out': 'tax1Amt', 'type':'Double'},
            {'in': 'taxAmount',           'out': 'taxAmount', 'type':'Double'},
            {'in': 'taxCode',             'out': 'taxCode', 'type':'RecordRef'},
            {'in': 'taxDetailsReference', 'out': 'taxDetailsReference', 'type':'String'},
            {'in': 'taxRate1',            'out': 'taxRate1', 'type':'Double'},
            {'in': 'taxRate2',            'out': 'taxRate2', 'type':'Double'},
            {'in': 'unitDisp',            'out': 'unitDisp', 'type':'String'},
        ],
    },

    'promotionsList': {
        'node_names': ['promotions'],
        'column_map': [
            {'in': 'couponCode',          'out': 'couponCode', 'type':'RecordRef'},
            {'in': 'promoCode',           'out': 'promoCode', 'type':'RecordRef'},
        ],
    },

    'shipGroupList': {
        'node_names': ['shipGroup'],
        'column_map': [
            {'in': 'destinationAddress',  'out': 'destinationAddress', 'type':'String'},
            {'in': 'destinationAddressRef', 'out': 'destinationAddressRef', 'type':'RecordRef'},
            {'in': 'handlingRate',        'out': 'handlingRate', 'type':'Double'},
            {'in': 'handlingTax2Amt',     'out': 'handlingTax2Amt', 'type':'Double'},
            {'in': 'handlingTax2Rate',    'out': 'handlingTax2Rate', 'type':'String'},
            {'in': 'handlingTaxAmt',      'out': 'handlingTaxAmt', 'type':'Double'},
            {'in': 'handlingTaxCode',     'out': 'handlingTaxCode', 'type':'RecordRef'},
            {'in': 'handlingTaxRate',     'out': 'handlingTaxRate', 'type':'String'},
            {'in': 'id',                  'out': 'id', 'type':'Long'},
            {'in': 'isFulfilled',         'out': 'isFulfilled', 'type':'Boolean'},
            {'in': 'isHandlingTaxable',   'out': 'isHandlingTaxable', 'type':'Boolean'},
            {'in': 'isShippingTaxable',   'out': 'isShippingTaxable', 'type':'Boolean'},
            {'in': 'shippingMethod',      'out': 'shippingMethod', 'type':'String'},
            {'in': 'shippingMethodRef',   'out': 'shippingMethodRef', 'type':'RecordRef'},
            {'in': 'shippingRate',        'out': 'shippingRate', 'type':'Double'},
            {'in': 'shippingTax2Amt',     'out': 'shippingTax2Amt', 'type':'Double'},
            {'in': 'shippingTax2Rate',    'out': 'shippingTax2Rate', 'type':'String'},
            {'in': 'shippingTaxAmt',      'out': 'shippingTaxAmt', 'type':'Double'},
            {'in': 'shippingTaxCode',     'out': 'shippingTaxCode', 'type':'RecordRef'},
            {'in': 'shippingTaxRate',     'out': 'shippingTaxRate', 'type':'String'},
            {'in': 'sourceAddress',       'out': 'sourceAddress', 'type':'String'},
            {'in': 'sourceAddressRef',    'out': 'sourceAddressRef', 'type':'RecordRef'},
            {'in': 'weight',              'out': 'weight', 'type':'Double'},
        ],
    },

    'timeList': {
        'node_names': ['time'],
        'column_map': [
            {'in': 'amount',              'out': 'amount', 'type':'Double'},
            {'in': 'apply',               'out': 'apply', 'type':'Boolean'},
            {'in': 'billedDate',          'out': 'billedDate', 'type':'Timestamp'},
            {'in': 'class',               'out': 'class', 'type':'String'},
            {'in': 'department',          'out': 'department', 'type':'String'},
            {'in': 'doc',                 'out': 'doc', 'type':'Long'},
            {'in': 'employeeDisp',        'out': 'employeeDisp', 'type':'String'},
            {'in': 'grossAmt',            'out': 'grossAmt', 'type':'Double'},
            {'in': 'itemDisp',            'out': 'itemDisp', 'type':'String'},
            {'in': 'jobDisp',             'out': 'jobDisp', 'type':'String'},
            {'in': 'line',                'out': 'line', 'type':'Long'},
            {'in': 'location',            'out': 'location', 'type':'String'},
            {'in': 'memo',                'out': 'memo', 'type':'String'},
            {'in': 'quantity',            'out': 'quantity', 'type':'String'},
            {'in': 'rate',                'out': 'rate', 'type':'Double'},
            {'in': 'revRecEndDate',       'out': 'revRecEndDate', 'type':'Timestamp'},
            {'in': 'revRecSchedule',      'out': 'revRecSchedule', 'type':'RecordRef'},
            {'in': 'revRecStartDate',     'out': 'revRecStartDate', 'type':'Timestamp'},
            {'in': 'tax1Amt',             'out': 'tax1Amt', 'type':'Double'},
            {'in': 'taxAmount',           'out': 'taxAmount', 'type':'Double'},
            {'in': 'taxCode',             'out': 'taxCode', 'type':'RecordRef'},
            {'in': 'taxDetailsReference', 'out': 'taxDetailsReference', 'type':'String'},
            {'in': 'taxRate1',            'out': 'taxRate1', 'type':'Double'},
            {'in': 'taxRate2',            'out': 'taxRate2', 'type':'Double'},
            {'in': 'unitDisp',            'out': 'unitDisp', 'type':'String'},
        ],
    },

    'creditList': {
        'node_names': ['credit'],
        'column_map': [
            {'in': 'amount',              'out': 'amount', 'type':'Double'},
            {'in': 'appliedTo',           'out': 'applied_to', 'type':'String'},
            {'in': 'apply',               'out': 'apply', 'type':'Boolean'},
            {'in': 'creditDate',          'out': 'credit_date', 'type':'Timestamp'},
            {'in': 'currency',            'out': 'currency', 'type':'String'},
            {'in': 'doc',                 'out': 'doc', 'type':'Long'},
            {'in': 'due',                 'out': 'due', 'type':'Double'},
            {'in': 'job',                 'out': 'job', 'type':'String'},
            {'in': 'line',                'out': 'line', 'type':'Long'},
            {'in': 'refNum',              'out': 'ref_num', 'type':'String'},
            {'in': 'total',               'out': 'total', 'type':'Double'},
            {'in': 'type',                'out': 'type', 'type':'String'},
        ],
    },
}
