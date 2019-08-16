from meltano.core.compiler.project_compiler import ProjectCompiler
from meltano.core.plugin_discovery_service import (
    PluginDiscoveryService,
    PluginNotFoundError,
)
from meltano.core.plugin import PluginType
from meltano.core.project import Project
from meltano.core.project_add_service import ProjectAddService
from meltano.core.config_service import ConfigService
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.tracking import GoogleAnalyticsTracker

from flask import Blueprint, request, jsonify

pluginsBP = Blueprint("plugins", __name__, url_prefix="/api/v1/plugins")


@pluginsBP.route("/all", methods=["GET"])
def all():
    new_project = Project()
    new_plugin_discovery_service = PluginDiscoveryService(new_project)
    result = new_plugin_discovery_service.discover(PluginType.ALL)
    return jsonify(result)


@pluginsBP.route("/installed", methods=["GET"])
def installed():
    """Returns JSON of all installed plugins

    Fuses the discovery.yml data with meltano.yml data
    """

    project = Project.find()
    config = ConfigService(project)
    discovery = PluginDiscoveryService(project)
    meltano_manifest = project.meltano
    installedPlugins = {}
    plugins = []

    for plugin in config.plugins():
        try:
            definition = discovery.find_plugin(plugin.type, plugin.name)
        except PluginNotFoundError:
            definition = {}

        merged_plugin_definition = {**definition.canonical(), **plugin.canonical()}
        merged_plugin_definition.pop("settings", None)
        merged_plugin_definition.pop("select", None)

        plugins.append(merged_plugin_definition)

    for type in meltano_manifest["plugins"]:
        installedPlugins[type] = []
        for type_plugin in meltano_manifest["plugins"][type]:
            for complete_plugin in plugins:
                if type_plugin["name"] == complete_plugin["name"]:
                    installedPlugins[type].append(complete_plugin)

    meltano_manifest["plugins"] = installedPlugins

    return jsonify(meltano_manifest)


@pluginsBP.route("/add", methods=["POST"])
def add():
    payload = request.get_json()
    plugin_type = PluginType(payload["plugin_type"])
    plugin_name = payload["name"]

    project = Project.find()
    add_service = ProjectAddService(project)
    plugin = add_service.add(plugin_type, plugin_name)

    return jsonify(plugin.canonical())


@pluginsBP.route("/install/batch", methods=["POST"])
def install_batch():
    payload = request.get_json()
    plugin_type = PluginType(payload["plugin_type"])
    plugin_name = payload["name"]

    project = Project.find()
    discovery = PluginDiscoveryService(project)
    target_plugin = discovery.find_plugin(plugin_type, plugin_name)

    config_service = ConfigService(project)
    add_service = ProjectAddService(project)
    install_service = PluginInstallService(project)
    ignored_types = [target_plugin.type, PluginType.TRANSFORMS]
    has_model = False
    batched = []
    for plugin in discovery.plugins():
        if plugin.namespace == target_plugin.namespace:
            if plugin.type not in ignored_types:
                add_service.add(plugin.type, plugin.name)
                plugin_install = config_service.find_plugin(
                    plugin.name, plugin_type=plugin.type
                )
                batched.append(plugin_install.canonical())
                run_venv = install_service.create_venv(plugin_install)
                run_install_plugin = install_service.install_plugin(plugin_install)
                if plugin.type is PluginType.MODELS:
                    has_model = True

    if has_model:
        compiler = ProjectCompiler(project)
        try:
            compiler.compile()
        except Exception as e:
            pass

    return jsonify(batched)


@pluginsBP.route("/install", methods=["POST"])
def install():
    payload = request.get_json()
    plugin_type = PluginType(payload["plugin_type"])
    plugin_name = payload["name"]

    project = Project.find()
    compiler = ProjectCompiler(project)
    install_service = PluginInstallService(project)
    config_service = ConfigService(project)

    plugin = config_service.find_plugin(plugin_name, plugin_type=plugin_type)
    run_venv = install_service.create_venv(plugin)
    run_install_plugin = install_service.install_plugin(plugin)

    if plugin_type is PluginType.MODELS:
        try:
            compiler.compile()
        except Exception as e:
            pass

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_add(plugin_type=plugin_type, plugin_name=plugin_name)

    return jsonify(plugin.canonical())
