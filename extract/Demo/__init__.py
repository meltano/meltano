import pandas as pd
from sqlalchemy import MetaData, Table, String, Column, TIMESTAMP, Float, Integer

demo_metadata = MetaData()
users_table = Table(
    'users',  # Name of the table
    demo_metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    schema='demo'
)

products_table = Table(
    'products',  # Name of the table
    demo_metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('price', Float),
    schema='demo'
)
carts_table = Table(
    'carts',
    demo_metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer),
    Column('product_id', Integer),
    Column('qty', Integer),
    Column('created_at', TIMESTAMP),
    schema='demo'
)


class DemoExtractor:
    """
    Demo Extractor
    """
    def __init__(self):
        self.name = 'demo'
        self.tables = {
            'users': users_table,
            'products': products_table,
            'carts': carts_table,
        }
        self.primary_keys = {
            'users': ['id'],
            'products': ['id'],
            'carts': ['id'],
        }
        self.entities = ['users', 'products', 'carts']
        self.TEST_DATA = {
            'users': [
                {'id': 1, 'name': 'jacob'},
                {'id': 2, 'name': 'josh'},
                {'id': 3, 'name': 'alex'},
                {'id': 4, 'name': 'micael'},
                {'id': 5, 'name': 'yannis'},
            ],
            'products': [
                {'id': 1, 'name': 'apple', 'price': 1.32},
                {'id': 2, 'name': 'lemon', 'price': 2.12},
                {'id': 3, 'name': 'orange', 'price': 2.45},
                {'id': 4, 'name': 'melon', 'price': 1.98},
                {'id': 5, 'name': 'appricot', 'price': 0.96},
            ],
            'carts': [
                {'id': 1, 'user_id': 1, 'product_id': 1, 'qty': 5, 'created_at': '2018-04-12 10:01:50'},
                {'id': 2, 'user_id': 1, 'product_id': 5, 'qty': 3, 'created_at': '2018-04-23 15:35:40'},
                {'id': 3, 'user_id': 2, 'product_id': 2, 'qty': 2, 'created_at': '2018-05-01 12:13:25'},
                {'id': 4, 'user_id': 3, 'product_id': 4, 'qty': 6, 'created_at': '2018-05-17 08:51:31'},
                {'id': 5, 'user_id': 3, 'product_id': 3, 'qty': 2, 'created_at': '2018-06-08 21:12:08'},
                {'id': 6, 'user_id': 4, 'product_id': 4, 'qty': 3, 'created_at': '2018-07-13 16:49:37'},
                {'id': 7, 'user_id': 5, 'product_id': 5, 'qty': 4, 'created_at': '2018-07-25 14:17:12'},
                {'id': 8, 'user_id': 5, 'product_id': 1, 'qty': 7, 'created_at': '2018-08-06 20:25:52'},
            ]

        }

    def extract(self, entity):
        yield pd.DataFrame(data=self.TEST_DATA.get(entity))
