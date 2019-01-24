from flask import Blueprint, jsonify, request
from .settings_helper import SettingsHelper

settingsBP = Blueprint("settings", __name__, url_prefix="/settings")


@settingsBP.route("/", methods=["GET"])
def index():
    settings_helper = SettingsHelper()
    return jsonify(settings_helper.get_connections())


@settingsBP.route("/save", methods=["POST"])
def save():
    settings_helper = SettingsHelper()
    connection = request.get_json()
    settings = settings_helper.save_connection(connection)
    return jsonify(settings)


@settingsBP.route("/delete", methods=["POST"])
def delete():
    settings_helper = SettingsHelper()
    connection = request.get_json()
    settings = settings_helper.delete_connection(connection)
    return jsonify(settings)


@settingsBP.route("/connections/<name>/test")
def test(name):
    current_settings = Settings.query.first().settings
    connections = current_settings["connections"]
    try:
        found_connection = next(
            connection for connection in connections if connection["name"] == name
        )
    # this is a really broad exception catch, this will swallow sneaky errors
    except Exception as e:
        found_connection = {}

    return jsonify(found_connection)
