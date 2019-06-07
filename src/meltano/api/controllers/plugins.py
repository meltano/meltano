from meltano.core.compiler.project_compiler import ProjectCompiler
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.plugin import PluginType
from meltano.core.project import Project
from meltano.core.project_add_service import ProjectAddService
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.tracking import GoogleAnalyticsTracker

from flask import Blueprint, request, jsonify

pluginsBP = Blueprint(
    "plugins", __name__, url_prefix="/api/v1/plugins"
)


@pluginsBP.route("/all", methods=["GET"])
def all():
    new_project = Project()
    new_plugin_discovery_service = PluginDiscoveryService(new_project)
    result = new_plugin_discovery_service.discover(PluginType.ALL)
    return jsonify(result)


@pluginsBP.route("/installed", methods=["GET"])
def installed():
    project = Project.find()
    return jsonify(project.meltano)


@pluginsBP.route("/install", methods=["POST"])
def install():
    project = Project.find()
    add_service = ProjectAddService(project)
    plugin_collection_type = request.get_json()["collectionType"]
    plugin_name = request.get_json()["name"]
    plugin = add_service.add(plugin_collection_type, plugin_name)
    install_service = PluginInstallService(project)
    run_venv = install_service.create_venv(plugin)
    run_install_plugin = install_service.install_plugin(plugin)

    compiler = ProjectCompiler(project)
    try:
        compiler.compile()
    except Exception as e:
        pass

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_add(
        plugin_type=plugin_collection_type, plugin_name=plugin_name
    )

    return jsonify({"test": 123})
