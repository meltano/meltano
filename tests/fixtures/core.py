import pytest
import os
import shutil

from meltano.core.project_init_service import ProjectInitService
from meltano.core.project_add_service import ProjectAddService
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.config_service import ConfigService
from meltano.core.plugin import PluginType


PROJECT_NAME = "a_meltano_project"


@pytest.fixture
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
    }


@pytest.fixture(scope="class")
def project_init_service():
    return ProjectInitService(PROJECT_NAME)


@pytest.fixture
def plugin_discovery_service(project, discovery):
    return PluginDiscoveryService(
        project, discovery=discovery
    )  # TODO: discovery factory


@pytest.fixture
def project_add_service(project, plugin_discovery_service):
    return ProjectAddService(project, plugin_discovery_service=plugin_discovery_service)


@pytest.fixture
def config_service(project):
    return ConfigService(project)


@pytest.fixture(scope="class")
def project(test_dir, project_init_service):
    project = project_init_service.init()

    # this is a test repo, let's remove the `.env`
    os.unlink(project.root.joinpath(".env"))

    # cd into the new project root
    project.activate()
    yield project

    # clean-up
    os.chdir(test_dir)
    shutil.rmtree(project.root)
