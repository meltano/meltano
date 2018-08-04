import os
import json
import typing

import requests
from sqlalchemy.orm import sessionmaker

from __main__ import api_key_name
from elt.db import DB
from elt.utils import get_basic_auth
from schema import Charge, Customer, Dispute, Product, Refund

PAGE_SIZE = 100
API_ROOT = 'https://api.stripe.com/v1'
CHARGES_LIST_URI = '/charges'
CUSTOMERS_LIST_URI = '/customers'
DISPUTES_LIST_URI = '/disputes'
PRODUCTS_LIST_URI = '/products'
REFUNDS_LIST_URI = '/refunds'

DB.setup()
engine = DB.engine()
Session = sessionmaker(bind=engine)
session = Session()

auth = get_basic_auth(os.getenv(api_key_name), '')


class Extractor:
    def __init__(self, args, start_time: int, end_time: int):
        """
        :param args: cli args
        :param start_time: epoch int timestamp
        :param end_time: epoch int timestamp
        """
        self.args = args
        self.start_time = start_time
        self.end_time = end_time
        self.limit = PAGE_SIZE

    def get_resource(
            self, endpoint_uri: str,
            starting_after_object_id: str = None,
            schema=None,
    ) -> typing.Tuple[dict, bool]:
        """
        General handler for the stripe API list resources.
        Handles extraction of the given resource type (e.g. Charge, Refund...)
        with the limit and start & end date set at the instance init stage from the cli args.
        :api_endpoint: `/charges`, `/refunds` endpoint of the resource
        :starting_after: id of the object after which results must be given (pagination)
        https://stripe.com/docs/api/curl#pagination

        :return: (data from this request, more results for pagination)
        """
        payload = {
            'limit': self.limit,
            'created[gt]': self.start_time,
            'created[lt]': self.end_time,
        }
        # add pagination
        if starting_after_object_id:
            payload['starting_after'] = starting_after_object_id
        # add expanding of fields
        expand_fields = getattr(schema, '_expand_fields', False)
        if expand_fields:
            payload['expand[]'] = expand_fields

        resp = requests.get(
            API_ROOT + endpoint_uri,
            params=payload,
            auth=auth,
        )
        resp.raise_for_status()
        resp_dict = resp.json()
        return (resp_dict['data'], resp_dict.get('has_more', False))

    def get_all_w_pagination(self, endpoint_uri: str, schema: object = None) -> typing.List:
        """
        Go over API pagination and extract all of the items for the given method (e.g. Charges, Customers)
        :endpoint_uri:
        :return: generator of items chunks with max len == PAGE_SIZE
        """
        items, has_more = self.get_resource(endpoint_uri, schema=schema)
        while True:
            if len(items) > 0:
                yield items
            if has_more is False:
                break
            else:
                last_charge_in_chunk_id = items[-1].get('id', None)
                items, has_more = self.get_resource(endpoint_uri, starting_after_object_id=last_charge_in_chunk_id)

    @staticmethod
    def transform(item: dict, model) -> dict:
        """
        Main data transformation is happening here,
        1) Transforms item to the format expected by the DB
        2) Dictionary values are stored as JSON in the DB
        :param model: Model object that is being transformed - it must implement get_substitution_map()
        :param item: instance of the dict to be transformed
        :return: items that are ready to be inserted to the DB
        """
        substitutions = model.get_substitution_map()
        if substitutions:
            for old_key, new_key in substitutions.items():
                item[new_key] = item.pop(old_key)
        item_fields = model.get_data_fields()
        transformed_dict = {}
        for key, val in item.items():
            if key in item_fields:
                if type(val) == dict:
                    transformed_dict[key] = json.dumps(val)
                elif type(val) == list and len(val) > 0:
                    transformed_dict[key] = str(val)
                else:
                    transformed_dict[key] = val
        return transformed_dict

    def load(self) -> None:
        """
        For each of the resources paginate over all pages and add data to the DW
        """
        # Charges
        for page in self.get_all_w_pagination(endpoint_uri=CHARGES_LIST_URI, schema=Charge):
            for charge in page:
                transformed_charge = self.transform(charge, Charge)
                session.merge(
                    Charge(**transformed_charge)
                )
            session.commit()
        # Customers
        for page in self.get_all_w_pagination(endpoint_uri=CUSTOMERS_LIST_URI, schema=Customer):
            for customer in page:
                transformed_customer = self.transform(customer, Customer)
                session.merge(
                    Customer(**transformed_customer)
                )
            session.commit()
        # Disputes
        for page in self.get_all_w_pagination(endpoint_uri=DISPUTES_LIST_URI, schema=Dispute):
            for dispute in page:
                transformed_dispute = self.transform(dispute, Dispute)
                session.merge(
                    Dispute(**transformed_dispute)
                )
            session.commit()
        # Products
        for page in self.get_all_w_pagination(endpoint_uri=PRODUCTS_LIST_URI, schema=Product):
            for product in page:
                transformed_product = self.transform(product, Product)
                session.merge(
                    Product(**transformed_product)
                )
            session.commit()
        # Refunds
        for page in self.get_all_w_pagination(endpoint_uri=REFUNDS_LIST_URI, schema=Refund):
            for refund in page:
                transformed_refund = self.transform(refund, Refund)
                session.merge(
                    Refund(**transformed_refund)
                )
            session.commit()
