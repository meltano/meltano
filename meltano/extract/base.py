from abc import ABC, abstractmethod


class MeltanoExtractor:

    def __init__(self):
        pass

    @abstractmethod
    def extract(self):
        """
        Return all the extracted entities supported by the extractor

        Return format: list of {'EntityName': String, 'DataFrame': } dictionaries

        Example:
        [{'EntityName': 'users', 'DataFrame': PANDAS_DATA_FRAME_FOR_USERS},
         {'EntityName': 'items', 'DataFrame': PANDAS_DATA_FRAME_FOR_ITEMS},
         {'EntityName': 'carts', 'DataFrame': PANDAS_DATA_FRAME_FOR_CARTS}]

        Return a DataFrame for a specified entity.
        """
        pass
