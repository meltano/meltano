from pyhocon import ConfigFactory
from pathlib import Path

class MeltanoAnalysisFileParserMissingFieldsError(Exception):
    def __init__(self, fields, cls, file_name, *args):
        self.file_name = file_name
        self.cls = cls
        field = "field" if len(fields) == 1  else "fields"
        self.message = f"Missing {field} in {cls}: \"{', '.join(fields)}\" in {self.file_name}"
        super(MeltanoAnalysisFileParserMissingFieldsError, self).__init__(self.message, self.file_name, *args)

    def __str__(self):
        return f"{self.message} in {self.file_name}"

    def __repr__(self):
        return f"{self.message} in {self.file_name}"

class MeltanoAnalysisFileParserError(Exception):
    def __init__(self, message, file_name, *args):
        self.message = message
        self.file_name = file_name
        super(MeltanoAnalysisFileParserError, self).__init__(self.message, self.file_name, *args)

class MeltanoAnalysisFileParser:
    
    def __init__(self, directory):
        self.directory = directory
        self.models = []
        self.required_model_properties = ['name', 'connection', 'label', 'explores']
        self.required_explore_properties = ['from', 'label', 'description']

    def missing_properties(self, properties, properties_dict):
        properties_copy = properties.copy()
        for prop in properties_dict:
            try:
              property_index = properties_copy.index(prop)
              del properties_copy[property_index]
            except ValueError as e:
              continue
        return properties_copy

    def parse(self):
        structure = {}
        ma_models = Path(self.directory).glob("*.model.ma")
        ma_dashboards = Path(self.directory).glob("*.dashboards.ma")
        for model in ma_models:
            file_name = model.parts[-1]
            try:
              conf = ConfigFactory.parse_string(open(model,'r').read())
            except MeltanoAnalysisFileParserMissingFieldsError as e:
              raise MeltanoAnalysisFileParserError(e.message, file_name)
            self.models.append(conf)

    def model(self, data, file_name):
        this_model = {}
        missing_properties = self.missing_properties(self.required_model_properties, data)
        if missing_properties:
            raise MeltanoAnalysisFileParserMissingFieldsError(missing_properties, 'model', file_name)
        for prop in data:
            this_model[prop] = data[prop]
            if prop == 'explores':
                this_model[prop] = self.explores(data[prop], file_name)
        return this_model


    def explores(self, explores, file_name):
        model_explores = []
        for explore in explores:
            this_explore = {}
            this_explore['name'] = explore
            missing_properties = self.missing_properties(self.required_explore_properties, explores[explore])
            if missing_properties:
                raise MeltanoAnalysisFileParserMissingFieldsError(missing_properties, 'explore', file_name)
            for prop in explores[explore]:
                this_explore[prop] = explores[explore][prop]
            model_explores.append(this_explore)
        return model_explores

    def views(self):
        pass

    def dimensions(self):
        pass

    def measures(self):
        pass

    def join(self):
        pass
        