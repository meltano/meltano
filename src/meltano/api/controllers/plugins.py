from meltano.core.project import Project
from meltano.core.config_service import ConfigService

from flask import Blueprint, request, url_for, jsonify, make_response, Response

pluginsBP = Blueprint(
    "plugins", __name__, url_prefix="/api/v1/plugins"
)


@pluginsBP.route("/get/all", methods=["GET"])
def get_all():
    project = Project()
    plugins = ConfigService(project).plugins()
    return jsonify(plugins)
