import os

import pytest
from snowplow_tracker import Emitter

from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.tracking.snowplow_tracker import get_snowplow_tracker


@pytest.mark.meta
def test_tracking_disabled(project):
    assert os.getenv("MELTANO_DISABLE_TRACKING") == "True"
    assert ProjectSettingsService(project).get("send_anonymous_usage_stats") is False


def test_get_snowplow_tracker(project):
    endpoints = '["http://mycollector:8080"]'
    ProjectSettingsService(project).set("snowplow.collector_endpoints", endpoints)

    tracker = get_snowplow_tracker(project, "some-user-id")

    assert tracker.subject.standard_nv_pairs["uid"] == "some-user-id"
    assert isinstance(tracker.emitters[0], Emitter)
    assert tracker.emitters[0].endpoint == "http://mycollector:8080/i"


def test_get_snowplow_tracker_no_endpoints(project):
    # Project fixture has no snowplow.collector_endpoints
    with pytest.raises(ValueError, match="is empty"):
        get_snowplow_tracker(project)
