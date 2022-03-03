import logging
import os

import pytest
from snowplow_tracker import Emitter, Subject

from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.tracking.snowplow_tracker import SnowplowTracker


@pytest.mark.meta
def test_tracking_disabled(project):
    assert os.getenv("MELTANO_DISABLE_TRACKING") == "True"
    assert ProjectSettingsService(project).get("send_anonymous_usage_stats") is False


def test_get_snowplow_tracker(project):
    endpoints = '["http://mycollector:8080"]'
    ProjectSettingsService(project).set("snowplow.collector_endpoints", endpoints)

    subject = Subject()
    subject.set_user_id("some-user-id")

    tracker = SnowplowTracker(project, subject=subject, namespace="cli")

    assert tracker.standard_nv_pairs["tna"] == "cli"  # namespace
    assert tracker.standard_nv_pairs["aid"] is None  # app_id
    assert tracker.subject.standard_nv_pairs["uid"] == "some-user-id"
    assert isinstance(tracker.emitters[0], Emitter)
    assert tracker.emitters[0].endpoint == "http://mycollector:8080/i"


def test_get_snowplow_tracker_invalid_endpoint(project, caplog):
    endpoints = """
        [
            "notvalid:8080",
            "https://valid.endpoint:8080",
            "file://bad.scheme"
        ]
    """
    ProjectSettingsService(project).set("snowplow.collector_endpoints", endpoints)

    with caplog.at_level(logging.WARNING, logger="snowplow_tracker.emitters"):
        tracker = SnowplowTracker(project)

    assert len(caplog.records) == 2
    assert caplog.records[0].levelname == "WARNING"
    assert caplog.records[0].msg["event"] == "invalid_snowplow_endpoint"
    assert caplog.records[0].msg["endpoint"] == "notvalid:8080"

    assert caplog.records[1].levelname == "WARNING"
    assert caplog.records[1].msg["event"] == "invalid_snowplow_endpoint"
    assert caplog.records[1].msg["endpoint"] == "file://bad.scheme"

    assert isinstance(tracker.emitters[0], Emitter)
    assert len(tracker.emitters) == 1
    assert tracker.emitters[0].endpoint == "https://valid.endpoint:8080/i"


def test_get_snowplow_tracker_no_endpoints(project):
    # Project fixture has no snowplow.collector_endpoints
    with pytest.raises(ValueError, match="is empty"):
        SnowplowTracker(project)
