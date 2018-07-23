import json
import os
import pandas as pd

from itertools import count
from meltano.load.base import MeltanoLoader
from meltano.common.service import MeltanoService
from meltano.common.entity import Entity


class JSONLoader(MeltanoLoader):
    def __init__(self, *args):
        self.filenames = dict()
        super().__init__(*args)

    def filename(self, basename):
        """
        Generates a sequential filename for a basename.

        <basename> → <basename>.<seq>.json
        """
        if basename not in self.filenames:
            self.filenames[basename] = (
                ".".join((basename, "{:04}".format(i), "json")) \
                for i in count()
            )

        return next(self.filenames[basename])

    def load(self, source_name, entity: Entity, data):
        data.to_json(self.filename(entity.alias), orient='records')


MeltanoService.register_loader("com.meltano.load.json", JSONLoader)
