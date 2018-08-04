from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import String, Boolean, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base

from __main__ import args

Base = declarative_base()


class Charge(Base):
    __tablename__ = 'charges'
    __table_args__ = {"schema": args.schema}
    id = Column(String, primary_key=True)
    amount = Column(Integer)
    amount_refunded = Column(Integer)
    application = Column(String)
    application_fee = Column(String)
    balance_transaction = Column(String)
    captured = Column(Boolean)
    created = Column(Integer)
    currency = Column(String)
    customer = Column(String)
    description = Column(String)
    destination = Column(String)
    dispute = Column(String)
    failure_code = Column(String)
    failure_message = Column(String)
    invoice = Column(String)
    charge_metadata = Column(JSON)
    on_behalf_of = Column(String)
    order = Column(String)
    outcome = Column(JSON)
    paid = Column(Boolean)
    receipt_number = Column(String)
    refunded = Column(Boolean)
    refunds = Column(JSON)
    review = Column(String)
    statement_descriptor = Column(String)
    status = Column(String)
    transfer = Column(String)
    transfer_group = Column(String)

    @classmethod
    def get_data_fields(cls):
        return [attr for attr in cls.__dict__ if not attr.startswith('_')]

    @staticmethod
    def get_substitution_map():
        return {
            'metadata': 'charge_metadata',
        }


class Customer(Base):
    __tablename__ = 'customers'
    __table_args__ = {"schema": args.schema}
    id = Column(String, primary_key=True)
    account_balance = Column(Integer)
    created = Column(Integer)
    currency = Column(String)
    discount = Column(JSON)
    default_source = Column(String)
    delinquent = Column(Boolean)
    description = Column(String)
    customer_metadata = Column(JSON)
    subscriptions = Column(JSON)
    # string that would be passed as a request param to expand returned objects
    # https://stripe.com/docs/api#expanding_objects
    _expand_fields = 'data.discount'

    @classmethod
    def get_data_fields(cls):
        return [attr for attr in cls.__dict__ if not attr.startswith('_')]

    @staticmethod
    def get_substitution_map():
        return {
            'metadata': 'customer_metadata',
        }


class Dispute(Base):
    __tablename__ = 'disputes'
    __table_args__ = {"schema": args.schema}
    id = Column(String, primary_key=True)
    amount = Column(Integer)
    balance_transactions = Column(JSON)
    charge = Column(String)
    created = Column(Integer)
    currency = Column(String)
    is_charge_refundable = Column(Boolean)
    dispute_metadata = Column(JSON)
    reason = Column(String)
    status = Column(String)

    @classmethod
    def get_data_fields(cls):
        return [attr for attr in cls.__dict__ if not attr.startswith('_')]

    @staticmethod
    def get_substitution_map():
        return {
            'metadata': 'dispute_metadata',
        }


class Product(Base):
    __tablename__ = 'products'
    __table_args__ = {"schema": args.schema}
    id = Column(String, primary_key=True)
    active = Column(Boolean)
    attributes = Column(String)
    caption = Column(String)
    created = Column(Integer)
    deactivate_on = Column(String)
    description = Column(String)
    images = Column(String)
    product_metadata = Column(JSON)
    name = Column(String)
    statement_descriptor = Column(String)
    type = Column(String)
    unit_label = Column(String)
    updated = Column(Integer)
    url = Column(String)

    @classmethod
    def get_data_fields(cls):
        return [attr for attr in cls.__dict__ if not attr.startswith('_')]

    @staticmethod
    def get_substitution_map():
        return {
            'metadata': 'product_metadata',
        }


class Refund(Base):
    __tablename__ = 'refunds'
    __table_args__ = {"schema": args.schema}
    id = Column(String, primary_key=True)
    amount = Column(Integer)
    balance_transaction = Column(String)
    charge = Column(String)
    created = Column(Integer)
    currency = Column(String)
    failure_balance_transaction = Column(String)
    failure_reason = Column(String)
    refund_metadata = Column(JSON)
    reason = Column(String)
    receipt_number = Column(String)
    status = Column(String)

    @classmethod
    def get_data_fields(cls):
        return [attr for attr in cls.__dict__ if not attr.startswith('_')]

    @staticmethod
    def get_substitution_map():
        return {
            'metadata': 'refund_metadata',
        }
