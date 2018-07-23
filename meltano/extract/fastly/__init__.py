from meltano.common.service import MeltanoService
from .extractor import FastlyExtractor


MeltanoService.register_extractor("com.meltano.extract.fastly", FastlyExtractor)
