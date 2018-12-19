from pyhocon import ConfigFactory
from pathlib import Path
from jinja2 import Template

class MeltanoAnalysisFileParserMissingViewError(Exception):
    def __init__(self, field, your_choice, cls, file_name, *args):
        self.file_name = file_name
        self.cls = cls
        self.message = f"Missing accompanying view \"{your_choice}\" in \"{field}\" field in {cls} in {file_name}."
        super(MeltanoAnalysisFileParserMissingViewError, self).__init__(self.message, self.file_name, *args)

class MeltanoAnalysisFileParserUnacceptableChoiceError(Exception):
    def __init__(self, field, your_choice, acceptable_choices, cls, file_name, *args):
        self.file_name = file_name
        self.cls = cls
        quoted_choices = [f"\"{a}\"" for a in acceptable_choices]
        self.message = f"Unacceptable choice for field {field}. You wrote \"{your_choice}\". Acceptable choices are: {', '.join(quoted_choices)}. In {file_name}"
        super(MeltanoAnalysisFileParserUnacceptableChoiceError, self).__init__(self.message, self.file_name, *args)

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
        self.required_join_properties = ['sql_on', 'relationship']
        self.required_view_properties = ['sql_table_name', 'dimensions']
        self.join_relationship_types = ['one_to_one', 'one_to_many', 'many_to_one', 'many_to_many']

    def uses_accepted_choice(self, choices, choice):
        return choice in choices

    def missing_properties(self, properties, properties_dict):
        properties_copy = properties.copy()
        for prop in properties_dict:
            try:
              property_index = properties_copy.index(prop)
              del properties_copy[property_index]
            except ValueError as e:
              continue
        return properties_copy

    def parse_ma_file(self, file_path):
        return ConfigFactory.parse_string(open(file_path,'r').read())

    def parse(self):
        self.ma_views = Path(self.directory).glob("*.view.ma")
        self.ma_models = Path(self.directory).glob("*.model.ma")
        self.ma_dashboards = Path(self.directory).glob("*.dashboards.ma")
        for model in self.ma_models:
            file_name = model.parts[-1]
            try:
                conf = self.parse_ma_file(model)
                parsed_model = self.model(conf, file_name)
            except MeltanoAnalysisFileParserMissingFieldsError as e:
                raise MeltanoAnalysisFileParserError(e.message, file_name)
            except MeltanoAnalysisFileParserUnacceptableChoiceError as e:
                raise MeltanoAnalysisFileParserError(e.message, file_name)
            except MeltanoAnalysisFileParserMissingViewError as e:
                raise MeltanoAnalysisFileParserError(e.message, file_name)
            self.models.append(parsed_model)
        return self.models

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

    def view_conf_by_name(self, view_name, cls, prop, file_name):
        try:
            return next(view for view in self.ma_views if view.parts[-1] == f"{view_name}.view.ma")
        except StopIteration as e:
            raise MeltanoAnalysisFileParserMissingViewError(prop, view_name, cls, file_name)

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
                if prop == 'from':
                    matching_view = self.view_conf_by_name(this_explore[prop], 'explore', prop, file_name)
                    this_explore['related_view'] = self.view(self.parse_ma_file(matching_view), file_name)
                if prop == 'joins':
                    this_explore[prop] = self.joins(explores[explore][prop], file_name)
            model_explores.append(this_explore)
        return model_explores

    def joins(self, joins, file_name):
        explore_joins = []
        for join in joins:
            this_join = {}
            this_join['name'] = join
            missing_properties = self.missing_properties(self.required_join_properties, joins[join])
            if missing_properties:
                raise MeltanoAnalysisFileParserMissingFieldsError(missing_properties, 'join', file_name)
            for prop in joins[join]:
                this_join[prop] = joins[join][prop]
                if prop == 'relationship':
                    uses_accepted_choices = self.uses_accepted_choice(self.join_relationship_types, joins[join][prop])
                    if not uses_accepted_choices:
                        raise MeltanoAnalysisFileParserUnacceptableChoiceError(prop, joins[join][prop], self.join_relationship_types, 'join', file_name)

            explore_joins.append(this_join)
        return explore_joins

    def view(self, view_file, file_name):
        this_view = {}
        missing_properties = self.missing_properties(self.required_view_properties, view_file)
        if missing_properties:
            raise MeltanoAnalysisFileParserMissingFieldsError(missing_properties, 'view', file_name)
        for prop in view_file:
            this_view[prop] = view_file[prop]
            if prop == 'dimensions':
                this_view[prop] = self.dimensions(view_file[prop])
            elif prop == 'measures':
                this_view[prop] = self.measures(view_file[prop])
        return this_view

    def dimensions(self, dimensions):
        this_dimensions = {}
        for dimension in dimensions:
            this_dimensions[dimension] = {}
            for prop in dimensions[dimension]:
                this_dimensions[dimension][prop] = dimensions[dimension][prop]
        return this_dimensions

    def measures(self, measures):
        this_measure = {}
        for measure in measures:
            this_measure[measure] = {}
            for prop in measures[measure]:
                this_measure[measure][prop] = measures[measure][prop]
        return this_measure

    def join(self):
        pass
        