from flask import Blueprint, jsonify, request
from .settingshelper import SettingsHelper

settingsBP = Blueprint("settings", __name__, url_prefix="/settings")


@settingsBP.route("/", methods=["GET"])
def index():
    settingsHelper = SettingsHelper()
    return jsonify(settingsHelper.get_connections())


@settingsBP.route("/new", methods=["POST"])
def new():
    settingsHelper = SettingsHelper()
    settings = request.get_json()
    settingsHelper.set_connections(settings)
    return jsonify(settings)


@settingsBP.route("/delete", methods=["POST"])
def delete():
    settingsHelper = SettingsHelper()
    settings = request.get_json()
    settings = settingsHelper.delete_connection(settings)
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
