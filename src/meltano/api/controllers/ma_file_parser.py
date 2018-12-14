from pyhocon import HOCONConverter
from pathlib import Path

class MeltanoAnalysisFileParserMissingFieldError(Exception):
    def __init__(self, message, file_name, *args):
        self.message = f"Missing field {message}"
        self.file_name = file_name
        super(MeltanoAnalysisFileParserMissingFieldError, self).__init__(self.message, self.file_name, *args)

class MeltanoAnalysisFileParserError(Exception):
    def __init__(self, message, file_name, *args):
        self.message = message
        self.file_name = file_name
        super(MeltanoAnalysisFileParserError, self).__init__(message, file_name, *args)

class MeltanoAnalysisFileParser:
    
    def __init__(self, directory):
        self.directory = directory
        self.models = []

    def parse(self):
        structure = {}
        ma_models = Path(self.directory).glob("*.model.ma")
        ma_dashboards = Path(self.directory).glob("*.dashboards.ma")
        for model in ma_models:
            file_name = model.parts[-1]
            try:
              conf = HOCONConverter.convert_from_file(model)
              self.model(conf, file_name)
            except Exception as e:
              raise MeltanoAnalysisFileParserError(str(e), file_name)
            self.models.append(conf)

    def model(self, data, file_name):
        this_model = {}
        try:
          this_model["name"] = data["name"]
        except Exception as e:
          raise MeltanoAnalysisFileParserMissingFieldError("name", file_name)

    def explores(self):
        pass

    def views(self):
        pass

    def dimensions(self):
        pass

    def measures(self):
        pass

    def join(self):
        pass



            

        