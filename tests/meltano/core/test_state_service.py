import pytest

from meltano.core.state_service import StateService


class TestStateService:
    @pytest.fixture
    def state_service(self, session):
        # TODO: Add job history to db
        yield session

    def test_get_state(self, state_services):
        """TODO: docstring

        Args:


        Returns:
        """

        NotImplemented

    def test_get_or_create_job(self, state_service):
        # TODO
        NotImplemented

    def test_list_state(self, state_service):
        # TODO
        NotImplemented

    def test_set_state(self, state_service):
        """TODO: docstring

        Args:


        Returns:
        """
        NotImplemented

    def test_clear_state(self, state_service):
        """TODO: docstring

        Args:


        Returns:
        """
        NotImplemented
