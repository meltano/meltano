from flask import Blueprint, jsonify, request

settingsBP = Blueprint("settings", __name__, url_prefix="/settings")

from ..app import db

from ..models.settings import Settings


@settingsBP.route("/", methods=["GET"])
def index():
    settings = Settings.query.first()
    if not settings:
        settings = Settings()
    return jsonify(settings.serializable())


@settingsBP.route("/new", methods=["POST"])
def new():
    settings = request.get_json()
    current_settings = Settings.query.first()
    if not current_settings:
        current_settings = Settings()
    current_settings.settings = settings
    db.session.add(current_settings)
    db.session.commit()
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
