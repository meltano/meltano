from __future__ import annotations

import json

from meltano.core.project import Project


class SettingsHelper:
    def __init__(self):
        project = Project.find()
        self.settings_file_path = project.root_dir("model", "database.settings.m5o")
        if not self.settings_file_path.is_file():
            with open(self.settings_file_path, "w") as f:
                settings = {"settings": {"connections": []}}
                json.dump(settings, f)

    def get_connections(self):
        with open(self.settings_file_path) as f:
            settings_file = json.load(f)
        return settings_file

    def save_connection(self, connection):
        with open(self.settings_file_path) as f:
            settings = json.load(f)
        settings["settings"]["connections"].append(connection)
        with open(self.settings_file_path, "w") as f:
            json.dump(settings, f)
        return settings

    def delete_connection(self, connection):
        with open(self.settings_file_path) as f:
            settings = json.load(f)
        connections = settings["settings"]["connections"]
        updated_connections = [
            conn for conn in connections if conn["name"] != connection["name"]
        ]
        settings["settings"]["connections"] = updated_connections
        with open(self.settings_file_path, "w") as f:
            json.dump(settings, f)
        return settings
