import io
import logging
import pandas as pd
import numpy as np
import json
import asyncio
import itertools

from pandas.io.json import json_normalize
from meltano.extract.base import MeltanoExtractor

class DemoExtractor(MeltanoExtractor):
    """
    Demo Extractor
    """

    def entities(self):
        """
        Return a list of Entities supported by this Extractor.

        Whatever type the extractor wants as long as it is properly used in
         extract_entity()
        """
        return ['users', 'products', 'carts']

    def extract_entity(self, entity):
        """
        Return a DataFrame for a specified entity.
        """
        if entity == 'users':
            users = [
                {'id': 1, 'name': 'jacob'},
                {'id': 2, 'name': 'josh'},
                {'id': 3, 'name': 'alex'},
                {'id': 4, 'name': 'micael'},
                {'id': 5, 'name': 'yannis'},
            ]

            df = pd.DataFrame(data=users)
        elif entity == 'products':
            products = [
                {'id': 1, 'name': 'apple', 'price': 1.32},
                {'id': 2, 'name': 'lemon', 'price': 2.12},
                {'id': 3, 'name': 'orange', 'price': 2.45},
                {'id': 4, 'name': 'melon', 'price': 1.98},
                {'id': 5, 'name': 'appricot', 'price': 0.96},
            ]

            df = pd.DataFrame(data=products)
        elif entity == 'carts':
            carts = [
                {'id': 1, 'user_id': 1, 'product_id': 1, 'qty': 5, 'created_at': '2018-04-12 10:01:50'},
                {'id': 2, 'user_id': 1, 'product_id': 5, 'qty': 3, 'created_at': '2018-04-23 15:35:40'},
                {'id': 3, 'user_id': 2, 'product_id': 2, 'qty': 2, 'created_at': '2018-05-01 12:13:25'},
                {'id': 4, 'user_id': 3, 'product_id': 4, 'qty': 6, 'created_at': '2018-05-17 08:51:31'},
                {'id': 5, 'user_id': 3, 'product_id': 3, 'qty': 2, 'created_at': '2018-06-08 21:12:08'},
                {'id': 6, 'user_id': 4, 'product_id': 4, 'qty': 3, 'created_at': '2018-07-13 16:49:37'},
                {'id': 7, 'user_id': 5, 'product_id': 5, 'qty': 4, 'created_at': '2018-07-25 14:17:12'},
                {'id': 8, 'user_id': 5, 'product_id': 1, 'qty': 7, 'created_at': '2018-08-06 20:25:52'},
            ]

            df = pd.DataFrame(data=carts)
        else:
            raise ValueError("Not supported entity ({}) was provided".format(entity))

        return df

    def extract(self):
        result = []

        for entity in self.entities():
            result.append(
              {
                'EntityName': entity,
                'DataFrame': self.extract_entity(entity)
              }
            )

        return result
