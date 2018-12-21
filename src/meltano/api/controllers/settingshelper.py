import os
import json
from os.path import join
from pathlib import Path


class SettingsHelper:
    def __init__(self):
        self.meltano_model_path = join(os.getcwd(), "model")

        self.settings_file_path = Path(self.meltano_model_path).joinpath(
            "database.settings.ma"
        )
        if not self.settings_file_path.is_file():
            setting_file = open(self.settings_file_path, "w")
            setting_file.write(json.dumps({"settings": {"connections": []}}))
            setting_file.close()

    def get_connections(self):
        settings_file = json.loads(open(self.settings_file_path, "r").read())
        return settings_file

    def set_connections(self, contents):
        settings_file = open(self.settings_file_path, "w")
        settings_file.write(json.dumps({"settings": contents}))
        settings_file.close()

    def delete_connection(self, contents):
        settings_file = self.get_connections()
        settings = settings_file["settings"]
        connections = settings["connections"]
        updated_connections = [
            connection
            for connection in connections
            if connection["name"] != contents["name"]
        ]
        settings["connections"] = updated_connections
        self.set_connections({"connections": updated_connections})
        return settings
