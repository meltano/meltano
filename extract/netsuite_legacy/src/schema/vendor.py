from elt.schema import Schema, Column, DBType

from schema.utils import columns_from_mappings

PG_SCHEMA = 'netsuite'
PG_TABLE = 'vendors'
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
    {'in': 'accountNumber', 'out': 'account_number', 'type':'String'},
    {'in': 'addressbookList', 'out': 'addressbook_list', 'type':'Vendoraddressbooklist'},
    {'in': 'altEmail', 'out': 'alt_email', 'type':'String'},
    {'in': 'altName', 'out': 'alt_name', 'type':'String'},
    {'in': 'altPhone', 'out': 'alt_phone', 'type':'String'},
    {'in': 'balance', 'out': 'balance', 'type':'Double'},
    {'in': 'balancePrimary', 'out': 'balance_primary', 'type':'Double'},
    {'in': 'bcn', 'out': 'bcn', 'type':'String'},
    {'in': 'billPay', 'out': 'bill_pay', 'type':'Boolean'},
    {'in': 'category', 'out': 'category', 'type':'Recordref'},
    {'in': 'comments', 'out': 'comments', 'type':'String'},
    {'in': 'companyName', 'out': 'company_name', 'type':'String'},
    {'in': 'creditLimit', 'out': 'credit_limit', 'type':'Double'},
    {'in': 'currency', 'out': 'currency', 'type':'Recordref'},
    {'in': 'currencyList', 'out': 'currency_list', 'type':'Vendorcurrencylist'},
    {'in': 'customFieldList', 'out': 'custom_field_list', 'type':'Customfieldlist'},
    {'in': 'customForm', 'out': 'custom_form', 'type':'Recordref'},
    {'in': 'dateCreated', 'out': 'date_created', 'type':'Datetime'},
    {'in': 'defaultAddress', 'out': 'default_address', 'type':'String'},
    {'in': 'eligibleForCommission', 'out': 'eligible_for_commission', 'type':'Boolean'},
    {'in': 'email', 'out': 'email', 'type':'String'},
    {'in': 'emailPreference', 'out': 'email_preference', 'type':'Emailpreference'},
    {'in': 'emailTransactions', 'out': 'email_transactions', 'type':'Boolean'},
    {'in': 'entityId', 'out': 'entity_id', 'type':'String'},
    {'in': 'expenseAccount', 'out': 'expense_account', 'type':'Recordref'},
    {'in': 'fax', 'out': 'fax', 'type':'String'},
    {'in': 'faxTransactions', 'out': 'fax_transactions', 'type':'Boolean'},
    {'in': 'firstName', 'out': 'first_name', 'type':'String'},
    {'in': 'giveAccess', 'out': 'give_access', 'type':'Boolean'},
    {'in': 'globalSubscriptionStatus', 'out': 'global_subscription_status', 'type':'Globalsubscriptionstatus'},
    {'in': 'homePhone', 'out': 'home_phone', 'type':'String'},
    {'in': 'image', 'out': 'image', 'type':'Recordref'},
    {'in': 'incoterm', 'out': 'incoterm', 'type':'Recordref'},
    {'in': 'is1099Eligible', 'out': 'is1099_eligible', 'type':'Boolean'},
    {'in': 'isAccountant', 'out': 'is_accountant', 'type':'Boolean'},
    {'in': 'isInactive', 'out': 'is_inactive', 'type':'Boolean'},
    {'in': 'isJobResourceVend', 'out': 'is_job_resource_vend', 'type':'Boolean'},
    {'in': 'isPerson', 'out': 'is_person', 'type':'Boolean'},
    {'in': 'laborCost', 'out': 'labor_cost', 'type':'Double'},
    {'in': 'lastModifiedDate', 'out': 'last_modified_date', 'type':'Datetime'},
    {'in': 'lastName', 'out': 'last_name', 'type':'String'},
    {'in': 'legalName', 'out': 'legal_name', 'type':'String'},
    {'in': 'middleName', 'out': 'middle_name', 'type':'String'},
    {'in': 'mobilePhone', 'out': 'mobile_phone', 'type':'String'},
    {'in': 'openingBalance', 'out': 'opening_balance', 'type':'Double'},
    {'in': 'openingBalanceAccount', 'out': 'opening_balance_account', 'type':'Recordref'},
    {'in': 'openingBalanceDate', 'out': 'opening_balance_date', 'type':'Datetime'},
    {'in': 'password', 'out': 'password', 'type':'String'},
    {'in': 'password2', 'out': 'password2', 'type':'String'},
    {'in': 'payablesAccount', 'out': 'payables_account', 'type':'Recordref'},
    {'in': 'phone', 'out': 'phone', 'type':'String'},
    {'in': 'phoneticName', 'out': 'phonetic_name', 'type':'String'},
    {'in': 'pricingScheduleList', 'out': 'pricing_schedule_list', 'type':'Vendorpricingschedulelist'},
    {'in': 'printOnCheckAs', 'out': 'print_on_check_as', 'type':'String'},
    {'in': 'printTransactions', 'out': 'print_transactions', 'type':'Boolean'},
    {'in': 'purchaseOrderAmount', 'out': 'purchase_order_amount', 'type':'Double'},
    {'in': 'purchaseOrderQuantity', 'out': 'purchase_order_quantity', 'type':'Double'},
    {'in': 'purchaseOrderQuantityDiff', 'out': 'purchase_order_quantity_diff', 'type':'Double'},
    {'in': 'receiptAmount', 'out': 'receipt_amount', 'type':'Double'},
    {'in': 'receiptQuantity', 'out': 'receipt_quantity', 'type':'Double'},
    {'in': 'receiptQuantityDiff', 'out': 'receipt_quantity_diff', 'type':'Double'},
    {'in': 'representingSubsidiary', 'out': 'representing_subsidiary', 'type':'Recordref'},
    {'in': 'requirePwdChange', 'out': 'require_pwd_change', 'type':'Boolean'},
    {'in': 'rolesList', 'out': 'roles_list', 'type':'Vendorroleslist'},
    {'in': 'salutation', 'out': 'salutation', 'type':'String'},
    {'in': 'sendEmail', 'out': 'send_email', 'type':'Boolean'},
    {'in': 'subscriptionsList', 'out': 'subscriptions_list', 'type':'Subscriptionslist'},
    {'in': 'subsidiary', 'out': 'subsidiary', 'type':'Recordref'},
    {'in': 'taxIdNum', 'out': 'tax_id_num', 'type':'String'},
    {'in': 'taxItem', 'out': 'tax_item', 'type':'Recordref'},
    {'in': 'terms', 'out': 'terms', 'type':'Recordref'},
    {'in': 'title', 'out': 'title', 'type':'String'},
    {'in': 'unbilledOrders', 'out': 'unbilled_orders', 'type':'Double'},
    {'in': 'unbilledOrdersPrimary', 'out': 'unbilled_orders_primary', 'type':'Double'},
    {'in': 'url', 'out': 'url', 'type':'String'},
    {'in': 'vatRegNumber', 'out': 'vat_reg_number', 'type':'String'},
    {'in': 'workCalendar', 'out': 'work_calendar', 'type':'Recordref'},
]

