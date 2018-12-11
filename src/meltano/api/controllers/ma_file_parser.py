from pyhocon import HOCONConverter
from pathlib import Path

class MeltanoAnalysisFileParserError(Exception):
    pass

class MeltanoAnalysisFileParser:
    
    def __init__(self, directory):
        self.directory = directory
        self.models = []

    def parse(self):
        structure = {}
        ma_models = Path(self.directory).glob("*.model.ma")
        ma_dashboards = Path(self.directory).glob("*.dashboards.ma")
        for model in ma_models:
            try:
              conf = HOCONConverter.convert_from_file(model)
              self.models.append(conf)
            except Exception as e:
              raise MeltanoAnalysisFileParserError(e)

    def models(self, data):


    def explores(self):
        pass


            

        