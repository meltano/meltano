import io
import logging
import pandas as pd
import numpy as np
import json
import asyncio
import itertools

from pandas.io.json import json_normalize
from meltano.schema import DBType
from meltano.extract.base import MeltanoExtractor
from meltano.common.transform import columnify
from meltano.common.entity import Entity, Attribute, TransientAttribute

class DemoExtractor(MeltanoExtractor):
    """
    Demo Extractor
    """

    def entities(self):
        print('')
        print('DemoExtractor > entities')
        print('')

        return ['entity1', 'entity2', 'entity3']

    def extract(self, entity):
        print('')
        print('DemoExtractor > extract {}'.format(entity))
        print('')

        return 'Extraction Result for {}'.format(entity)

    def extract_all(self):
        print('')
        print('DemoExtractor > extract_all')
        print('')

        result = []

        for entity in self.entities():
            result.append(self.extract(entity))

        return result
