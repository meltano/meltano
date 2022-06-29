import logging

from snowplow_tracker import Emitter

from meltano.core.tracking import Tracker


def test_get_snowplow_tracker_invalid_endpoint(project, caplog, monkeypatch):
    endpoints = """
        [
            "notvalid:8080",
            "https://valid.endpoint:8080",
            "file://bad.scheme",
            "https://other.endpoint/path/to/collector"
        ]
    """
    monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", endpoints)
    logging.getLogger().setLevel(logging.DEBUG)

    with caplog.at_level(logging.WARNING, logger="snowplow_tracker.emitters"):
        tracker = Tracker(project)

    try:
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
            tracker.snowplow_tracker.emitters[0].endpoint
            == "https://valid.endpoint:8080/i"
        )

        assert isinstance(tracker.snowplow_tracker.emitters[1], Emitter)
        assert (
            tracker.snowplow_tracker.emitters[1].endpoint
            == "https://other.endpoint/path/to/collector/i"
        )
    finally:
        # Remove the seemingly valid emitters to prevent a logging error on exit.
        tracker.snowplow_tracker.emitters = []
