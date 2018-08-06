from abc import ABC, abstractmethod
from pandas import DataFrame

from meltano.common.entity import Entity


class MeltanoLoader(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def schema_apply(self, manifest: str):
        """
        Load the schema manifest from a file (or str) and create/update the schema
        in the target Data Warehouse
        """
        pass

    @abstractmethod
    def load(self, entity_name: str, dataframe: DataFrame):
        """
        Load the data in the provided dataframe to table schema_name.entity_name
        """
        pass
