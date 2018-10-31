import pytest

from meltano.core.project_init_service import ProjectInitService


PROJECT_NAME = "a_meltano_project"


@pytest.fixture
def project_init_service():
    return ProjectInitService()


@pytest.fixture(scope="class")
def project(test_dir):
    service = ProjectInitService(PROJECT_NAME)
    project = service.init()

    # cd into the new project root
    project.chdir()
    return project
