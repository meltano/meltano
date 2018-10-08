from os import environ as env
import pytest

from tap_marketo.client import *
from tap_marketo.marketo_utils import *


# Set up a pytest namespace so that data can be passed between tests
def pytest_namespace():
    return {}


class TestMarketoUtils:
    def test_create_keyfile(self):
        marketo_utils = MarketoUtils(env.copy())
        config_dict = marketo_utils.generate_keyfile(minute_offset=60, output_file=None)
        assert list(config_dict.keys()) == ['endpoint', 'identity', 'client_id', 'client_secret', 'start_time']
        pytest.config_dict = config_dict
        pytest.marketo_utils = marketo_utils

    def test_generate_start_time(self):
        run_time = '2018-10-01T01:00:00.000000'
        expected_output = '2018-10-01T00:00:00Z'
        actual_output = pytest.marketo_utils.generate_start_time(offset=60, run_time=run_time)


class TestMarketoClient:
    def test_init_class(self):
        marketo_client = MarketoClient(pytest.config_dict)
        assert marketo_client.access_token is not None
        assert marketo_client.start_time_token is not None
        pytest.client = marketo_client

    def test_get_activity_types(self):
        activity_types = pytest.client.get_activity_types()
        assert type(activity_types) == list
        assert type(activity_types[0]) == dict
        pytest.activity_types = [activity_types[0]['id']]

    def test_get_activities(self):
        activities = pytest.client.get_activities(pytest.activity_types)
        assert type(activities) == list
        assert type(activities[0]) == dict
        pytest.activities = [activities[0]['leadId']]

    def test_get_leads(self):
        leads = pytest.client.get_leads(pytest.activities)
        assert type(leads) == list
        assert type(leads[0]) == dict
        pytest.leads = leads
