from pyhocon import ConfigFactory
from pathlib import Path
from jinja2 import Template

import logging
import json


class MeltanoAnalysisFileParserError(Exception):
    def __init__(self, message, file_name, *args):
        self.message = message
        self.file_name = file_name
        super(MeltanoAnalysisFileParserError, self).__init__(
            self.message, self.file_name, *args
        )


class MeltanoAnalysisFileParserMissingTableError(MeltanoAnalysisFileParserError):
    def __init__(self, field, your_choice, cls, file_name, *args):
        self.file_name = file_name
        self.cls = cls
        self.message = f'Missing accompanying table "{your_choice}" in "{field}" field in {cls} in {file_name}.'
        super(MeltanoAnalysisFileParserMissingTableError, self).__init__(
            self.message, self.file_name, *args
        )


class MeltanoAnalysisFileParserUnacceptableChoiceError(MeltanoAnalysisFileParserError):
    def __init__(self, field, your_choice, acceptable_choices, cls, file_name, *args):
        self.file_name = file_name
        self.cls = cls
        quoted_choices = [f'"{a}"' for a in acceptable_choices]
        self.message = f"Unacceptable choice for field {field}. You wrote \"{your_choice}\". Acceptable choices are: {', '.join(quoted_choices)}. In {file_name}"
        super(MeltanoAnalysisFileParserUnacceptableChoiceError, self).__init__(
            self.message, self.file_name, *args
        )


class MeltanoAnalysisFileParserMissingFieldsError(MeltanoAnalysisFileParserError):
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


class MeltanoAnalysisFileParser:
    def __init__(self, directory):
        self.directory = directory
        self.models = []
        self.required_model_properties = ["name", "connection", "label", "designs"]
        self.required_design_properties = ["from", "label", "description"]
        self.required_join_properties = ["sql_on", "relationship"]
        self.required_table_properties = ["sql_table_name", "columns"]
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

    def parse_m5o_file(self, file_path):
        try:
            return ConfigFactory.parse_string(open(file_path, "r").read())
        except Exception as e:
            raise MeltanoAnalysisFileParserError(str(e), str(file_path.parts[-1]))

    def compile(self, models):
        indices = {}
        for model in models:
            compiled_file_name = f"{model['name']}.model.m5oc"
            compiled_file_path = Path(self.directory).joinpath(compiled_file_name)
            compiled_model = open(compiled_file_path, "w")
            indices[model["name"]] = {"designs": [e["name"] for e in model["designs"]]}
            compiled_model.write(json.dumps(model))
            compiled_model.close()

        # index file
        index_file_path = Path(self.directory).joinpath("models.index.m5oc")
        index_file = open(index_file_path, "w")
        index_file.write(json.dumps(indices))
        index_file.close()

    def parse(self):
        self.m5o_tables = list(Path(self.directory).glob("*.table.m5o"))
        self.m5o_models = list(Path(self.directory).glob("*.model.m5o"))
        self.m5o_dashboards = list(Path(self.directory).glob("*.dashboards.m5o"))
        for model in self.m5o_models:
            file_name = model.parts[-1]
            conf = self.parse_m5o_file(model)
            parsed_model = self.model(conf, file_name)
            self.models.append(parsed_model)

        return self.models

    def model(self, ma_file_model_dict, file_name):
        temp_model = {}
        missing_properties = self.missing_properties(
            self.required_model_properties, ma_file_model_dict
        )
        if missing_properties:
            raise MeltanoAnalysisFileParserMissingFieldsError(
                missing_properties, "model", file_name
            )
        for prop_name, prop_def in ma_file_model_dict.items():
            temp_model[prop_name] = prop_def
            if prop_name == "designs":
                temp_model[prop_name] = self.designs(prop_def, file_name)
        return temp_model

    def table_conf_by_name(self, table_name, cls, prop, file_name):
        try:
            return next(
                table
                for table in self.m5o_tables
                if table.parts[-1] == f"{table_name}.table.m5o"
            )
        except StopIteration as e:
            raise MeltanoAnalysisFileParserMissingTableError(
                prop, table_name, cls, file_name
            )

    def designs(self, ma_file_designs_dict, file_name):
        model_designs = []
        for design_name, design_def in ma_file_designs_dict.items():
            temp_design = {}
            temp_design["name"] = design_name
            missing_properties = self.missing_properties(
                self.required_design_properties, design_def
            )
            if missing_properties:
                raise MeltanoAnalysisFileParserMissingFieldsError(
                    missing_properties, "design", file_name
                )
            for prop_name, prop_def in design_def.items():
                temp_design[prop_name] = prop_def
                if prop_name == "from":
                    matching_table = self.table_conf_by_name(
                        temp_design[prop_name], "design", prop_name, file_name
                    )
                    temp_design["related_table"] = self.table(
                        self.parse_m5o_file(matching_table), matching_table.parts[-1]
                    )
                if prop_name == "joins":
                    temp_design[prop_name] = self.joins(prop_def, file_name)
            model_designs.append(temp_design)
        return model_designs

    def joins(self, ma_file_joins_dict, file_name):
        design_joins = []
        for join_name, join_def in ma_file_joins_dict.items():
            temp_join = {}
            temp_join["name"] = join_name
            related_table_name = join_def.get("from", join_name)
            matching_table = self.table_conf_by_name(
                related_table_name, "join", "name", file_name
            )
            temp_join["related_table"] = self.table(
                self.parse_m5o_file(matching_table), matching_table.parts[-1]
            )
            missing_properties = self.missing_properties(
                self.required_join_properties, join_def
            )
            if missing_properties:
                raise MeltanoAnalysisFileParserMissingFieldsError(
                    missing_properties, "join", file_name
                )
            for prop_name, prop_def in join_def.items():
                temp_join[prop_name] = prop_def
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

            design_joins.append(temp_join)
        return design_joins

    def table(self, table_file, file_name):
        temp_table = {}
        missing_properties = self.missing_properties(
            self.required_table_properties, table_file
        )
        if missing_properties:
            raise MeltanoAnalysisFileParserMissingFieldsError(
                missing_properties, "table", file_name
            )
        for prop_name, prop_def in table_file.items():
            subproperties = ("columns", "aggregates", "timeframes")

            if prop_name in subproperties:
                temp_table[prop_name] = self.name_flatten_dict(prop_def)
            else:
                temp_table[prop_name] = prop_def

        return temp_table

    @classmethod
    def name_flatten_dict(cls, d: Dict) -> List:
        return [{"name": k, **rest} for k, rest in d.items()]
