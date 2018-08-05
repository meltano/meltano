import pandas as pd
import asyncio
import logging

from typing import Sequence
from abc import ABC, abstractmethod


class MeltanoExtractor:

    def __init__(self):
        pass


    @abstractmethod
    def entities(self):
        """
        Generates a list of Entities supported by this Extractor.
        """
        pass


    @abstractmethod
    def extract(self, entity):
        """
        Generates DataFrames for a specified entity.
        """
        pass


    @abstractmethod
    def extract_all(self):
        """
        Generates DataFrames for all supported Entities.
        """
        pass

