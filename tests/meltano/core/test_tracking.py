import logging
import os

import pytest
from snowplow_tracker import Emitter

from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.tracking import Tracker


@pytest.mark.meta
def test_tracking_disabled(project):
    assert os.getenv("MELTANO_SEND_ANONYMOUS_USAGE_STATS") == "False"
    assert ProjectSettingsService(project).get("send_anonymous_usage_stats") is False


def test_get_snowplow_tracker_invalid_endpoint(project, caplog):
    endpoints = """
        [
            "notvalid:8080",
            "https://valid.endpoint:8080",
            "file://bad.scheme",
            "https://other.endpoint/path/to/collector"
        ]
    """
    ProjectSettingsService(project).set("snowplow.collector_endpoints", endpoints)

    with caplog.at_level(logging.WARNING, logger="snowplow_tracker.emitters"):
        tracker = Tracker(project)

    assert len(caplog.records) == 2
    assert caplog.records[0].levelname == "WARNING"
    assert caplog.records[0].msg["event"] == "invalid_snowplow_endpoint"
    assert caplog.records[0].msg["endpoint"] == "notvalid:8080"

    assert caplog.records[1].levelname == "WARNING"
    assert caplog.records[1].msg["event"] == "invalid_snowplow_endpoint"
    assert caplog.records[1].msg["endpoint"] == "file://bad.scheme"

    assert len(tracker.snowplow_tracker.emitters) == 2
    assert isinstance(tracker.snowplow_tracker.emitters[0], Emitter)
    assert (
        tracker.snowplow_tracker.emitters[0].endpoint == "https://valid.endpoint:8080/i"
    )

    assert isinstance(tracker.snowplow_tracker.emitters[1], Emitter)
    assert (
        tracker.snowplow_tracker.emitters[1].endpoint
        == "https://other.endpoint/path/to/collector/i"
    )
