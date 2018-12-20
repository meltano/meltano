from pyhocon import ConfigFactory
from pathlib import Path
from jinja2 import Template
import json


class MeltanoAnalysisFileParserMissingViewError(Exception):
    def __init__(self, field, your_choice, cls, file_name, *args):
        self.file_name = file_name
        self.cls = cls
        self.message = f'Missing accompanying view "{your_choice}" in "{field}" field in {cls} in {file_name}.'
        super(MeltanoAnalysisFileParserMissingViewError, self).__init__(
            self.message, self.file_name, *args
        )


class MeltanoAnalysisFileParserUnacceptableChoiceError(Exception):
    def __init__(self, field, your_choice, acceptable_choices, cls, file_name, *args):
        self.file_name = file_name
        self.cls = cls
        quoted_choices = [f'"{a}"' for a in acceptable_choices]
        self.message = f"Unacceptable choice for field {field}. You wrote \"{your_choice}\". Acceptable choices are: {', '.join(quoted_choices)}. In {file_name}"
        super(MeltanoAnalysisFileParserUnacceptableChoiceError, self).__init__(
            self.message, self.file_name, *args
        )


class MeltanoAnalysisFileParserMissingFieldsError(Exception):
    def __init__(self, fields, cls, file_name, *args):
        self.file_name = file_name
        self.cls = cls
        field = "field" if len(fields) == 1 else "fields"
        self.message = (
            f"Missing {field} in {cls}: \"{', '.join(fields)}\" in {self.file_name}"
        )
        super(MeltanoAnalysisFileParserMissingFieldsError, self).__init__(
            self.message, self.file_name, *args
        )

    def __str__(self):
        return f"{self.message} in {self.file_name}"

    def __repr__(self):
        return f"{self.message} in {self.file_name}"


class MeltanoAnalysisFileParserError(Exception):
    def __init__(self, message, file_name, *args):
        self.message = message
        self.file_name = file_name
        super(MeltanoAnalysisFileParserError, self).__init__(
            self.message, self.file_name, *args
        )


class MeltanoAnalysisFileParser:
    def __init__(self, directory):
        self.directory = directory
        self.models = []
        self.required_model_properties = ["name", "connection", "label", "explores"]
        self.required_explore_properties = ["from", "label", "description"]
        self.required_join_properties = ["sql_on", "relationship"]
        self.required_view_properties = ["sql_table_name", "dimensions"]
        self.join_relationship_types = [
            "one_to_one",
            "one_to_many",
            "many_to_one",
            "many_to_many",
        ]

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
        try:
            return ConfigFactory.parse_string(open(file_path, "r").read())
        except Exception as e:
            raise MeltanoAnalysisFileParserError(str(e), str(file_path.parts[-1]))

    def compile(self, models):
        indices = {}
        for model in models:
            compiled_file_name = f"{model['name']}.model.mac"
            compiled_file_path = Path(self.directory).joinpath(compiled_file_name)
            compiled_model = open(compiled_file_path, "w")
            indices[model["name"]] = {
                "explores": [e["name"] for e in model["explores"]]
            }
            compiled_model.write(json.dumps(model))
            compiled_model.close()

        # index file
        index_file_path = Path(self.directory).joinpath("models.index.mac")
        index_file = open(index_file_path, "w")
        index_file.write(json.dumps(indices))
        index_file.close()

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

    def model(self, ma_file_model_dict, file_name):
        this_model = {}
        missing_properties = self.missing_properties(
            self.required_model_properties, ma_file_model_dict
        )
        if missing_properties:
            raise MeltanoAnalysisFileParserMissingFieldsError(
                missing_properties, "model", file_name
            )
        for prop, prop_def in ma_file_model_dict.items():
            this_model[prop] = prop_def
            if prop == "explores":
                this_model[prop] = self.explores(prop_def, file_name)
        return this_model

    def view_conf_by_name(self, view_name, cls, prop, file_name):
        try:
            return next(
                view
                for view in self.ma_views
                if view.parts[-1] == f"{view_name}.view.ma"
            )
        except StopIteration as e:
            raise MeltanoAnalysisFileParserMissingViewError(
                prop, view_name, cls, file_name
            )

    def explores(self, ma_file_explores_dict, file_name):
        model_explores = []
        for explore_name, explore_def in ma_file_explores_dict.items():
            this_explore = {}
            this_explore["name"] = explore_name
            missing_properties = self.missing_properties(
                self.required_explore_properties, explore_def
            )
            if missing_properties:
                raise MeltanoAnalysisFileParserMissingFieldsError(
                    missing_properties, "explore", file_name
                )
            for prop_name, prop_def in explore_def.items():
                this_explore[prop_name] = prop_def
                if prop_name == "from":
                    matching_view = self.view_conf_by_name(
                        this_explore[prop_name], "explore", prop_name, file_name
                    )
                    this_explore["related_view"] = self.view(
                        self.parse_ma_file(matching_view), matching_view.parts[-1]
                    )
                if prop_name == "joins":
                    this_explore[prop_name] = self.joins(prop_def, file_name)
            model_explores.append(this_explore)
        return model_explores

    def joins(self, ma_file_joins_dict, file_name):
        explore_joins = []
        for join_name, join_def in ma_file_joins_dict.items():
            this_join = {}
            this_join["name"] = join_name
            matching_view = self.view_conf_by_name(
                this_join["name"], "join", "name", file_name
            )
            this_join["related_view"] = self.view(
                self.parse_ma_file(matching_view), matching_view.parts[-1]
            )
            missing_properties = self.missing_properties(
                self.required_join_properties, join_def
            )
            if missing_properties:
                raise MeltanoAnalysisFileParserMissingFieldsError(
                    missing_properties, "join", file_name
                )
            for prop_name, prop_def in join_def.items():
                this_join[prop_name] = prop_def
                if prop_name == "relationship":
                    uses_accepted_choices = self.uses_accepted_choice(
                        self.join_relationship_types, prop_def
                    )
                    if not uses_accepted_choices:
                        raise MeltanoAnalysisFileParserUnacceptableChoiceError(
                            prop_name,
                            prop_def,
                            self.join_relationship_types,
                            "join",
                            file_name,
                        )

            explore_joins.append(this_join)
        return explore_joins

    def view(self, view_file, file_name):
        this_view = {}
        missing_properties = self.missing_properties(
            self.required_view_properties, view_file
        )
        if missing_properties:
            raise MeltanoAnalysisFileParserMissingFieldsError(
                missing_properties, "view", file_name
            )
        for prop_name, prop_def in view_file.items():
            this_view[prop_name] = prop_def
            if prop_name == "dimensions":
                this_view[prop_name] = self.dimensions(prop_def)
            elif prop_name == "measures":
                this_view[prop_name] = self.measures(prop_def)
        return this_view

    def dimensions(self, ma_file_dimensions_dict):
        this_dimensions = {}
        for dimension_name, dimension_def in ma_file_dimensions_dict.items():
            this_dimensions[dimension_name] = {}
            for prop_name, prop_def in dimension_def.items():
                this_dimensions[dimension_name][prop_name] = prop_def
        return this_dimensions

    def measures(self, ma_file_measures_dict):
        this_measure = {}
        for measure_name, measure_def in ma_file_measures_dict.items():
            this_measure[measure_name] = {}
            for prop_name, prop_def in measure_def.items():
                this_measure[measure_name][prop_name] = prop_def
        return this_measure
