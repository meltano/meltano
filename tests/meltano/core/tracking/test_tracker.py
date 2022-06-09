import json
from unittest import mock

from meltano.core.tracking.tracker import TelemetrySettings, Tracker


class TestTracker:
    def test_telemetry_state_change_check(self, project):
        with mock.patch.object(Tracker, "save_telemetry_settings") as mocked_method:
            Tracker(project)
        assert mocked_method.call_count == 1

    def test_update_analytics_json(self, project):
        tracker = Tracker(project)
        inital_send_anonymous_usage_stats = tracker.send_anonymous_usage_stats

        # Check the inital value of `send_anonymous_usage_stats`
        with open(project.meltano_dir() / "analytics.json") as analytics_json_file:
            analytics_json_pre = json.load(analytics_json_file)
        assert (
            inital_send_anonymous_usage_stats
            == analytics_json_pre["send_anonymous_usage_stats"]
        )

        # Flip the value of `send_anonymous_usage_stats`
        tracker.send_anonymous_usage_stats = not inital_send_anonymous_usage_stats
        tracker.telemetry_state_change_check(
            TelemetrySettings(
                analytics_json_pre["client_id"],
                analytics_json_pre["project_id"],
                analytics_json_pre["send_anonymous_usage_stats"],
            )
        )

        # Ensure `send_anonymous_usage_stats` has been flipped on disk
        with open(project.meltano_dir() / "analytics.json") as analytics_json_file:
            analytics_json_post = json.load(analytics_json_file)
        assert (
            inital_send_anonymous_usage_stats
            != analytics_json_post["send_anonymous_usage_stats"]
        )
