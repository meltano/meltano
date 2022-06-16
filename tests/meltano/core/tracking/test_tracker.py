from __future__ import annotations

import json
import os
import uuid
from contextlib import contextmanager
from typing import Any
from unittest import mock

import pytest

from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.tracking.tracker import TelemetrySettings, Tracker
from meltano.core.utils import hash_sha256


def load_analytics_json(project: Project) -> dict[str, Any]:
    with open(project.meltano_dir() / "analytics.json") as analytics_json_file:
        return json.load(analytics_json_file)


def check_analytics_json(project: Project) -> None:
    analytics_json = load_analytics_json(project)

    for key in ("client_id", "project_id"):
        value = analytics_json[key]
        assert isinstance(value, str)
        uuid.UUID(value)

    assert isinstance(analytics_json["send_anonymous_usage_stats"], bool)


@contextmanager
def delete_analytics_json(project: Project) -> None:
    (project.meltano_dir() / "analytics.json").unlink()
    try:
        yield
    finally:
        # Recreate `analytics.json`, to avoid causing issues for other tests within the same class
        # that expect it. Note that `project` is class-scoped.
        Tracker(project)


def clear_telemetry_settings(project):
    ProjectSettingsService.config_override.pop("send_anonymous_usage_stats", None)
    os.environ.pop("MELTANO_SEND_ANONYMOUS_USAGE_STATS", None)
    setting_service = ProjectSettingsService(project)
    config = setting_service.meltano_yml_config
    config.pop("send_anonymous_usage_stats", None)
    setting_service.update_meltano_yml_config(config)


class TestTracker:
    def test_telemetry_state_change_check(self, project: Project):
        with mock.patch.object(Tracker, "save_telemetry_settings") as mocked:
            Tracker(project)
            assert mocked.call_count == 1

    def test_update_analytics_json(self, project: Project):
        tracker = Tracker(project)
        inital_send_anonymous_usage_stats = tracker.send_anonymous_usage_stats

        # Check the inital value of `send_anonymous_usage_stats`
        analytics_json_pre = load_analytics_json(project)
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
        analytics_json_post = load_analytics_json(project)
        assert (
            inital_send_anonymous_usage_stats
            != analytics_json_post["send_anonymous_usage_stats"]
        )

    def test_restore_project_id_from_analytics_json(self, project: Project):
        Tracker(project)  # Ensure `analytics.json` exists and is valid

        setting_service = ProjectSettingsService(project)
        original_project_id = setting_service.get("project_id")

        # Delete the project ID from `meltano.yml`, but leave it unchanged in `analytics.json`
        config = setting_service.meltano_yml_config
        del config["project_id"]
        setting_service.update_meltano_yml_config(config)

        assert setting_service.get("project_id") is None

        # Create a new `ProjectSettingsService` because it is what restores the project ID
        restored_project_id = ProjectSettingsService(project).get("project_id")

        assert original_project_id == restored_project_id

    def test_no_project_id_state_change_if_tracking_disabled(self, project: Project):
        clear_telemetry_settings(project)
        setting_service = ProjectSettingsService(project)
        method_name = "track_telemetry_state_change_event"

        setting_service.set("send_anonymous_usage_stats", True)
        setting_service.set("project_id", str(uuid.uuid4()))
        Tracker(project).save_telemetry_settings()

        setting_service.set("send_anonymous_usage_stats", False)
        with mock.patch.object(Tracker, method_name) as mocked:
            Tracker(project).save_telemetry_settings()
            assert mocked.call_count == 1

        setting_service.set("project_id", str(uuid.uuid4()))
        with mock.patch.object(Tracker, method_name) as mocked:
            Tracker(project).save_telemetry_settings()
            assert mocked.call_count == 0

    def test_no_state_change_event_without_analytics_json(self, project: Project):
        setting_service = ProjectSettingsService(project)
        method_name = "track_telemetry_state_change_event"

        setting_service.set("send_anonymous_usage_stats", True)
        setting_service.set("project_id", str(uuid.uuid4()))
        Tracker(project).save_telemetry_settings()

        with delete_analytics_json(project):
            setting_service.set("project_id", str(uuid.uuid4()))
            with mock.patch.object(Tracker, method_name) as mocked:
                Tracker(project)
                assert mocked.call_count == 0

    def test_analytics_json_is_created(self, project: Project):
        check_analytics_json(project)
        with delete_analytics_json(project):
            Tracker(project)
            check_analytics_json(project)

    @pytest.mark.parametrize(
        "analytics_json_content",
        [
            f'{{"clientId":"{str(uuid.uuid4())}","project_id":"{str(uuid.uuid4())}","send_anonymous_usage_stats":true}}',
            f'{{"client_id":"{str(uuid.uuid4())}","projectId":"{str(uuid.uuid4())}","send_anonymous_usage_stats":true}}',
            f'{{"client_id":"{str(uuid.uuid4())}","project_id":"{str(uuid.uuid4())}","send_anon_usage_stats":true}}',
            f'["{str(uuid.uuid4())}","{str(uuid.uuid4())}", true]',
            f'client_id":"{str(uuid.uuid4())}","project_id":"{str(uuid.uuid4())}","send_anonymous_usage_stats":true}}',
        ],
        ids=lambda param: hash_sha256(param)[:8],
    )
    def test_invalid_analytics_json_is_overwritten(
        self, project: Project, analytics_json_content: str
    ):
        with delete_analytics_json(project):
            # Use `delete_analytics_json` to ensure `analytics.json` is restored afterwards
            analytics_json_path = project.meltano_dir() / "analytics.json"
            with open(analytics_json_path, "w") as analytics_json_file:
                analytics_json_file.write(analytics_json_content)

            with pytest.raises(Exception):
                check_analytics_json(project)

            Tracker(project)

            check_analytics_json(project)

    def test_restore_project_id_and_telemetry_state_change(self, project: Project):
        """
        Test that `project_id` is restored from `analytics.json`, and a telemetry state change
        event is fired because `send_anonymous_usage_stats` is negated.
        """  # noqa: D205, D400
        Tracker(project)  # Ensure `analytics.json` exists and is valid

        setting_service = ProjectSettingsService(project)
        original_project_id = setting_service.get("project_id")

        # Delete the project ID from `meltano.yml`, but leave it unchanged in `analytics.json`
        config = setting_service.meltano_yml_config.copy()
        del config["project_id"]
        config["send_anonymous_usage_stats"] = not load_analytics_json(project)[
            "send_anonymous_usage_stats"
        ]
        setting_service.update_meltano_yml_config(config)

        assert setting_service.get("project_id") is None

        # Create a new `ProjectSettingsService` because it is what restores the project ID
        restored_project_id = ProjectSettingsService(project).get("project_id")

        assert original_project_id == restored_project_id

        with mock.patch.object(Tracker, "track_telemetry_state_change_event") as mocked:
            original_config_override = ProjectSettingsService.config_override
            try:
                ProjectSettingsService.config_override.pop(
                    "send_anonymous_usage_stats", None
                )
                Tracker(project)
                assert mocked.call_count == 1
            finally:
                ProjectSettingsService.config_override = original_config_override

    @pytest.mark.parametrize(
        "snowplow_endpoints,send_stats,expected",
        (
            (["https://example.com"], True, True),
            (["https://example.com"], False, False),
            ([], True, False),
            ([], False, False),
        ),
    )
    def test_can_track(
        self,
        project: Project,
        snowplow_endpoints: list[str],
        send_stats: bool,
        expected: bool,
    ):
        setting_service = ProjectSettingsService(project)
        setting_service.set("snowplow.collector_endpoints", snowplow_endpoints)
        setting_service.set("send_anonymous_usage_stats", send_stats)
        assert Tracker(project).can_track() is expected

    def test_send_anonymous_usage_stats(self, project: Project):
        clear_telemetry_settings(project)

        os.environ["MELTANO_SEND_ANONYMOUS_USAGE_STATS"] = "True"
        assert Tracker(project).send_anonymous_usage_stats is True

        # Ensure the env var takes priority
        ProjectSettingsService(project).set("send_anonymous_usage_stats", False)
        assert Tracker(project).send_anonymous_usage_stats is True

        os.environ["MELTANO_SEND_ANONYMOUS_USAGE_STATS"] = "False"
        assert Tracker(project).send_anonymous_usage_stats is False

        # Ensure the env var takes priority
        ProjectSettingsService(project).set("send_anonymous_usage_stats", True)
        assert Tracker(project).send_anonymous_usage_stats is False

        clear_telemetry_settings(project)
        ProjectSettingsService(project).set("send_anonymous_usage_stats", False)
        assert Tracker(project).send_anonymous_usage_stats is False

        clear_telemetry_settings(project)
        ProjectSettingsService(project).set("send_anonymous_usage_stats", True)
        assert Tracker(project).send_anonymous_usage_stats is True

    def test_default_send_anonymous_usage_stats(self, project: Project):
        clear_telemetry_settings(project)
        assert Tracker(project).send_anonymous_usage_stats

    @pytest.mark.parametrize("send_anonymous_usage_stats", (True, False))
    def test_context_with_telemetry_state_change_event(
        self, project: Project, send_anonymous_usage_stats: bool
    ):
        tracker = Tracker(project)
        tracker.send_anonymous_usage_stats = send_anonymous_usage_stats

        passed = False

        class MockSnowplowTracker:
            def track_unstruct_event(self, _, contexts):
                # Can't put asserts in here because this method is executed withing a try-except
                # block that catches all exceptions.
                nonlocal passed
                if send_anonymous_usage_stats:
                    passed = contexts is not None
                else:
                    passed = contexts is None

        tracker.snowplow_tracker = MockSnowplowTracker()

        tracker.track_telemetry_state_change_event(
            "project_id", uuid.uuid4(), uuid.uuid4()
        )
        assert passed

        tracker.track_telemetry_state_change_event(
            "send_anonymous_usage_stats", True, False
        )
        assert passed

        tracker.track_telemetry_state_change_event(
            "send_anonymous_usage_stats", False, True
        )
        assert passed
