from meltano.common.service import MeltanoService
from .extractor import DemoExtractor


MeltanoService.register_extractor("com.meltano.extract.demo", DemoExtractor)
