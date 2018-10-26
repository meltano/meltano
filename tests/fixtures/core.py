import pytest

from meltano.core.project_init_service import ProjectInitService


PROJECT_NAME = "a_meltano_project"


@pytest.fixture
def project_init_service():
    return ProjectInitService()


@pytest.fixture(scope="session")
def project(test_dir):
    service = ProjectInitService(PROJECT_NAME)
    return service.init()
