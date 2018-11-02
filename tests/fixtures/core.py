import pytest

from meltano.core.project_init_service import ProjectInitService
from meltano.core.project_add_service import ProjectAddService
from meltano.core.config_service import ConfigService


PROJECT_NAME = "a_meltano_project"


@pytest.fixture
def project_init_service():
    return ProjectInitService()


@pytest.fixture
def project_add_service(project):
    return ProjectAddService(project)


@pytest.fixture
def config_service(project):
    return ConfigService(project)


@pytest.fixture(scope="class")
def project(test_dir):
    service = ProjectInitService(PROJECT_NAME)
    project = service.init()

    # cd into the new project root
    project.chdir()
    return project
