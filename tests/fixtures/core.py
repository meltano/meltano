import pytest
import os
import shutil
import yaml

from pathlib import Path

from meltano.core.project_init_service import ProjectInitService
from meltano.core.project_add_service import ProjectAddService
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.config_service import ConfigService
from meltano.core.schedule_service import ScheduleService
from meltano.core.compiler.project_compiler import ProjectCompiler
from meltano.core.plugin import PluginType


PROJECT_NAME = "a_meltano_project"


@pytest.fixture()
def discovery():
    return {
        str(PluginType.EXTRACTORS): [{"name": "tap-mock", "pip_url": "tap-mock"}],
        str(PluginType.LOADERS): [{"name": "target-mock", "pip_url": "target-mock"}],
        str(PluginType.TRANSFORMERS): [
            {"name": "transformer-mock", "pip_url": "transformer-mock"}
        ],
        str(PluginType.TRANSFORMS): [
            {"name": "tap-mock-transform", "pip_url": "tap-mock-transform"}
        ],
        str(PluginType.MODELS): [{"name": "model-mock", "pip_url": "model-mock"}],
        str(PluginType.ORCHESTRATORS): [
            {"name": "orchestrator-mock", "pip_url": "orchestrator-mock"}
        ],
    }


@pytest.fixture()
def plugin_discovery_service(project, discovery):
    return PluginDiscoveryService(
        project, discovery=discovery
    )  # TODO: discovery factory


@pytest.fixture
def project_compiler(project):
    return ProjectCompiler(project)


@pytest.fixture(scope="class")
def project_init_service():
    return ProjectInitService(PROJECT_NAME)


@pytest.fixture(scope="class")
def plugin_install_service(project):
    return PluginInstallService(project)


@pytest.fixture(scope="class")
def project_add_service(project):
    return ProjectAddService(project)


@pytest.fixture(scope="class")
def add_model(project, plugin_install_service, project_add_service):
    plugin = project_add_service.add(PluginType.MODELS, "model-carbon-intensity-sqlite")
    plugin_install_service.create_venv(plugin)
    plugin_install_service.install_plugin(plugin)

    plugin = project_add_service.add(PluginType.MODELS, "model-gitflix")
    plugin_install_service.create_venv(plugin)
    plugin_install_service.install_plugin(plugin)

    plugin = project_add_service.add(PluginType.MODELS, "model-salesforce")
    plugin_install_service.create_venv(plugin)
    plugin_install_service.install_plugin(plugin)

    plugin = project_add_service.add(PluginType.MODELS, "model-gitlab")
    plugin_install_service.create_venv(plugin)
    plugin_install_service.install_plugin(plugin)


@pytest.fixture(scope="class")
def config_service(project):
    return ConfigService(project)


@pytest.fixture(scope="class")
def schedule_service(project):
    return ScheduleService(project)


@pytest.fixture(scope="class")
def project(test_dir, project_init_service):
    project = project_init_service.init()

    # this is a test repo, let's remove the `.env`
    os.unlink(project.root_dir(".env"))

    discovery_yaml = (
        Path(os.path.dirname(os.path.dirname(__file__)))
        .parent.joinpath("discovery.yml")
        .open("r")
        .read()
    )
    discovery_dict = yaml.load(discovery_yaml)
    discovery_dict[PluginType.EXTRACTORS].append(
        {"name": "tap-mock", "pip_url": "tap-mock"}
    )
    discovery_dict[PluginType.LOADERS].append(
        {"name": "target-mock", "pip_url": "target-mock"}
    )
    discovery_dict[PluginType.TRANSFORMERS].append(
        {"name": "transformer-mock", "pip_url": "transformer-mock"}
    )
    discovery_dict[PluginType.TRANSFORMS].append(
        {"name": "tap-mock-transform", "pip_url": "tap-mock-transform"}
    )
    discovery_dict[PluginType.MODELS].append(
        {
            "name": "model-gitlab",
            "pip_url": "git+https://gitlab.com/meltano/model-gitlab.git",
        }
    )
    # copy discovery.yml into this project
    with open(project.root.joinpath("discovery.yml"), "w") as f:
        yaml.dump(discovery_dict, f, default_flow_style=False)

    # cd into the new project root
    project.activate()
    os.chdir(project.root)

    yield project

    # clean-up
    os.chdir(test_dir)
    shutil.rmtree(project.root)
