from __future__ import annotations

import json
import subprocess
import typing as t
import uuid
from contextlib import contextmanager
from http import server as server_lib
from threading import Thread
from time import sleep
from unittest import mock

import pytest
from snowplow_tracker import Emitter

from meltano.core.tracking.contexts.cli import CliEvent
from meltano.core.tracking.contexts.environment import EnvironmentContext
from meltano.core.tracking.contexts.exception import ExceptionContext
from meltano.core.tracking.contexts.project import ProjectContext
from meltano.core.tracking.tracker import TelemetrySettings, Tracker, new_client_id
from meltano.core.utils import hash_sha256, new_project_id

if t.TYPE_CHECKING:
    from collections.abc import Generator

    from snowplow_tracker import SelfDescribing

    from fixtures.docker import SnowplowMicro
    from meltano.core.project import Project


def load_analytics_json(project: Project) -> dict[str, t.Any]:
    with project.meltano_dir().joinpath("analytics.json").open() as analytics_json_file:
        return json.load(analytics_json_file)


def check_analytics_json(project: Project) -> None:
    analytics_json = load_analytics_json(project)

    for key in ("client_id", "project_id"):
        value = analytics_json[key]
        assert isinstance(value, str)
        uuid.UUID(value)

    assert isinstance(analytics_json["send_anonymous_usage_stats"], bool)


@contextmanager
def delete_analytics_json(project: Project) -> Generator[None, None, None]:
    (project.meltano_dir() / "analytics.json").unlink(missing_ok=True)
    try:
        yield
    finally:
        Tracker(project)


class TestTracker:
    @pytest.fixture(autouse=True)
    def clear_telemetry_settings(self, project, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv("MELTANO_SEND_ANONYMOUS_USAGE_STATS", raising=False)
        config = project.settings.meltano_yml_config
        config.pop("send_anonymous_usage_stats", None)
        project.settings.update_meltano_yml_config(config)
        original_config_override = (
            type(project.settings).config_override.copy(),
            project.settings.config_override.copy(),
        )
        try:
            type(project.settings).config_override.clear()
            project.settings.config_override.clear()
            project.refresh()
            yield
        finally:
            (
                type(project.settings).config_override,
                project.settings.config_override,
            ) = original_config_override

    def test_telemetry_state_change_check(self, project: Project) -> None:
        with (
            mock.patch.object(
                Tracker,
                "save_telemetry_settings",
            ) as mocked,
            delete_analytics_json(project),
        ):
            Tracker(project)
            assert mocked.call_count == 1

    def test_update_analytics_json(self, project: Project) -> None:
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
            ),
        )

        # Ensure `send_anonymous_usage_stats` has been flipped on disk
        analytics_json_post = load_analytics_json(project)
        assert (
            inital_send_anonymous_usage_stats
            != analytics_json_post["send_anonymous_usage_stats"]
        )

    def test_restore_project_id_from_analytics_json(self, project: Project) -> None:
        Tracker(project)  # Ensure `analytics.json` exists and is valid

        original_project_id = project.settings.get("project_id")

        # Delete the project ID from `meltano.yml`,
        # but leave it unchanged in `analytics.json`
        config = project.settings.meltano_yml_config
        del config["project_id"]
        project.settings.update_meltano_yml_config(config)
        # The project refreshes itself once the config has been changed, which
        # creates a new `ProjectSettingsService`, restoring the `project_id`.
        restored_project_id = project.settings.get("project_id")

        # Depending on what tests were run before this one, the project ID
        # might have been randomly generated, or taken from `analytics.json`,
        # so we accept the restored one if it is equal to the original, or if
        # it is equal after the same transformation that gets applied to the
        # project ID when it is originally stored in `analytics.json`.
        assert original_project_id == restored_project_id or (
            str(uuid.UUID(hash_sha256(original_project_id)[::2])) == restored_project_id
        )

    def test_no_project_id_state_change_if_tracking_disabled(
        self,
        project: Project,
    ) -> None:
        method_name = "track_telemetry_state_change_event"

        project.settings.set("send_anonymous_usage_stats", value=True)
        project.settings.set("project_id", new_project_id())

        Tracker(project).save_telemetry_settings()

        project.settings.set("send_anonymous_usage_stats", value=False)
        with mock.patch.object(Tracker, method_name) as mocked:
            Tracker(project).save_telemetry_settings()
            assert mocked.call_count == 1

        project.settings.set("project_id", new_project_id())
        with mock.patch.object(Tracker, method_name) as mocked:
            Tracker(project).save_telemetry_settings()
            assert mocked.call_count == 0

    def test_no_state_change_event_without_analytics_json(
        self,
        project: Project,
    ) -> None:
        method_name = "track_telemetry_state_change_event"

        project.settings.set("send_anonymous_usage_stats", value=True)
        project.settings.set("project_id", new_project_id())
        Tracker(project).save_telemetry_settings()

        with delete_analytics_json(project):
            project.settings.set("project_id", new_project_id())
            with mock.patch.object(Tracker, method_name) as mocked:
                Tracker(project)
                assert mocked.call_count == 0

    def test_analytics_json_is_created(self, project: Project) -> None:
        Tracker(project)
        check_analytics_json(project)
        with delete_analytics_json(project):
            Tracker(project)
            check_analytics_json(project)

    @pytest.mark.parametrize(
        "analytics_json_content",
        (
            f'{{"clientId":"{new_client_id()!s}","project_id":"{new_project_id()!s}","send_anonymous_usage_stats":true}}',
            f'{{"client_id":"{new_client_id()!s}","projectId":"{new_project_id()!s}","send_anonymous_usage_stats":true}}',
            f'{{"client_id":"{new_client_id()!s}","project_id":"{new_project_id()!s}","send_anon_usage_stats":true}}',
            f'["{new_client_id()!s}","{new_project_id()!s}", true]',
            f'client_id":"{new_client_id()!s}","project_id":"{new_project_id()!s}","send_anonymous_usage_stats":true}}',
        ),
        ids=(0, 1, 2, 3, 4),
    )
    def test_invalid_analytics_json_is_overwritten(
        self,
        project: Project,
        analytics_json_content: str,
    ) -> None:
        with delete_analytics_json(project):
            # Use `delete_analytics_json` to ensure `analytics.json` is restored after
            analytics_json_path = project.meltano_dir() / "analytics.json"
            with analytics_json_path.open("w") as analytics_json_file:
                analytics_json_file.write(analytics_json_content)

            with pytest.raises((TypeError, KeyError, json.JSONDecodeError)):
                check_analytics_json(project)

            Tracker(project)

            check_analytics_json(project)

    def test_restore_project_id_and_telemetry_state_change(
        self,
        project: Project,
    ) -> None:
        """
        Test that `project_id` is restored from `analytics.json`, and a telemetry state
        change event is fired because `send_anonymous_usage_stats` is negated.
        """  # noqa: D205, D212
        Tracker(project)  # Ensure `analytics.json` exists and is valid

        original_project_id = project.settings.get("project_id")

        # Delete project ID from `meltano.yml`; leave it unchanged in `analytics.json`
        config = project.settings.meltano_yml_config.copy()
        del config["project_id"]
        config["send_anonymous_usage_stats"] = not load_analytics_json(project)[
            "send_anonymous_usage_stats"
        ]
        project.settings.update_meltano_yml_config(config)
        # The project refreshes itself once the config has been changed, which
        # creates a new `ProjectSettingsService`, restoring the `project_id`.
        restored_project_id = project.settings.get("project_id")

        # Depending on what tests were run before this one, the project ID
        # might have been randomly generated, or taken from `analytics.json`,
        # so we accept the restored one if it is equal to the original, or if
        # it is equal after the same transformation that gets applied to the
        # project ID when it is originally stored in `analytics.json`.
        assert original_project_id == restored_project_id or (
            str(uuid.UUID(hash_sha256(original_project_id)[::2])) == restored_project_id
        )

        with mock.patch.object(Tracker, "track_telemetry_state_change_event") as mocked:
            original_config_override = project.settings.config_override.copy()
            try:
                project.settings.config_override.pop("send_anonymous_usage_stats", None)
                Tracker(project)
                assert mocked.call_count == 1
            finally:
                project.settings.config_override = original_config_override

    @pytest.mark.parametrize(
        ("snowplow_endpoints", "send_stats", "expected"),
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
        *,
        snowplow_endpoints: list[str],
        send_stats: bool,
        expected: bool,
    ) -> None:
        project.settings.set("snowplow.collector_endpoints", snowplow_endpoints)
        project.settings.set("send_anonymous_usage_stats", send_stats)
        assert Tracker(project).can_track() is expected

    def test_send_anonymous_usage_stats(self, project: Project, monkeypatch) -> None:
        monkeypatch.setenv("MELTANO_SEND_ANONYMOUS_USAGE_STATS", "True")
        assert Tracker(project).send_anonymous_usage_stats is True

        # Ensure the env var takes priority
        project.settings.set("send_anonymous_usage_stats", value=False)
        assert Tracker(project).send_anonymous_usage_stats is True

        monkeypatch.setenv("MELTANO_SEND_ANONYMOUS_USAGE_STATS", "False")
        assert Tracker(project).send_anonymous_usage_stats is False

        # Ensure the env var takes priority
        project.settings.set("send_anonymous_usage_stats", value=True)
        assert Tracker(project).send_anonymous_usage_stats is False

    @pytest.mark.parametrize("setting_value", (False, True))
    def test_send_anonymous_usage_stats_no_env(
        self,
        project: Project,
        *,
        setting_value: bool,
    ) -> None:
        project.settings.set("send_anonymous_usage_stats", setting_value)
        assert Tracker(project).send_anonymous_usage_stats is setting_value

    def test_default_send_anonymous_usage_stats(self, project: Project) -> None:
        assert Tracker(project).send_anonymous_usage_stats

    @pytest.mark.usefixtures("project")
    def test_exit_event_is_fired(self, snowplow: SnowplowMicro) -> None:
        subprocess.run(("meltano", "invoke", "alpha-beta-fox"))

        event_summary = snowplow.all()
        assert event_summary["good"] > 0
        assert event_summary["bad"] == 0

        exit_event = next(
            x["event"]
            for x in snowplow.good()
            if x["event"]["event_name"] == "exit_event"
        )
        assert exit_event["unstruct_event"]["data"]["data"]["exit_code"] == 1

    @pytest.mark.parametrize("send_anonymous_usage_stats", (True, False))
    def test_context_with_telemetry_state_change_event(
        self,
        project: Project,
        *,
        send_anonymous_usage_stats: bool,
    ) -> None:
        tracker = Tracker(project)
        tracker.send_anonymous_usage_stats = send_anonymous_usage_stats

        passed = False

        class MockSnowplowTracker:
            def track(self, event: SelfDescribing) -> None:
                # Can't put asserts in here because this method is executed
                # withing a try-except block that catches all exceptions.
                nonlocal passed
                expected_contexts = [EnvironmentContext, ProjectContext]
                if send_anonymous_usage_stats:
                    expected_contexts.append(ExceptionContext)
                passed = len(set(event.context)) == len(expected_contexts) and all(
                    isinstance(ctx, tuple(expected_contexts)) for ctx in event.context
                )

        tracker.snowplow_tracker = MockSnowplowTracker()

        tracker.track_telemetry_state_change_event(
            "project_id",
            from_value=new_project_id(),
            to_value=new_project_id(),
        )
        assert passed

        tracker.track_telemetry_state_change_event(
            "send_anonymous_usage_stats",
            from_value=True,
            to_value=False,
        )
        assert passed

        tracker.track_telemetry_state_change_event(
            "send_anonymous_usage_stats",
            from_value=False,
            to_value=True,
        )
        assert passed

    @pytest.mark.order(0)
    @pytest.mark.parametrize(
        ("sleep_duration", "timeout_should_occur"),
        ((1.0, False), (5.0, True)),
        ids=("no_timeout", "timeout"),
    )
    def test_timeout_if_endpoint_unavailable(
        self,
        project: Project,
        sleep_duration,
        timeout_should_occur,
    ) -> None:
        """Test to ensure that the default tracker timeout is respected.

        An HTTP sever is run on another thread, which handles request sent from
        the Snowplow tracker. When `timeout_should_occur` is `False`, we check
        that this sever is properly masquerading as a Snowplow endpoint. When
        `timeout_should_occur` is `True`, we check that when the server takes
        too long to respond, we timeout and continue without raising an error.
        """

        class HTTPRequestHandler(server_lib.SimpleHTTPRequestHandler):
            def do_POST(self) -> None:
                sleep(sleep_duration)
                self.send_response(200, "OK")
                self.end_headers()

        with server_lib.HTTPServer(("localhost", 0), HTTPRequestHandler) as server:
            server_thread = Thread(
                target=server.serve_forever,
                kwargs={"poll_interval": 0.1},
            )

            project.settings.set(
                "snowplow.collector_endpoints",
                f'["http://localhost:{server.server_port}"]',
            )

            tracker = Tracker(project)
            assert tracker.snowplow_tracker is not None
            assert len(tracker.snowplow_tracker.emitters) == 1

            emitter = tracker.snowplow_tracker.emitters[0]
            assert isinstance(emitter, Emitter)
            emitter.on_failure = mock.MagicMock()

            server_thread.start()
            tracker.track_command_event(CliEvent.started)
            tracker.snowplow_tracker.flush()
            server.shutdown()
            server_thread.join()

            timeout_occurred = emitter.on_failure.call_count == 1
            assert timeout_occurred is timeout_should_occur

    def test_project_context_send_anonymous_usage_stats_source(
        self,
        project: Project,
        monkeypatch,
    ) -> None:
        def get_source():
            return ProjectContext(project, new_project_id()).to_json()["data"][
                "send_anonymous_usage_stats_source"
            ]

        assert get_source() == "default"

        project.settings.set(
            "send_anonymous_usage_stats",
            not project.settings.get("send_anonymous_usage_stats"),
        )
        assert get_source() == "meltano_yml"

        monkeypatch.setenv("MELTANO_SEND_ANONYMOUS_USAGE_STATS", "True")
        assert get_source() == "env"

    @pytest.mark.order(1)
    def test_get_snowplow_tracker_invalid_endpoint(
        self,
        project: Project,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        endpoints = """
            [
                "notvalid:8080",
                "https://valid.endpoint:8080",
                "file://bad.scheme",
                "https://other.endpoint/path/to/collector"
            ]
        """
        monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", endpoints)

        with pytest.warns(
            (UserWarning, UserWarning),
            # UserWarning,
            match="Invalid Snowplow endpoint",
        ) as warnings:
            tracker = Tracker(project)

        tracker_warnings = [
            w.message.args[0]
            for w in warnings
            if isinstance(w.message, UserWarning)
            and "Invalid Snowplow endpoint" in str(w.message)
        ]

        assert len(tracker_warnings) == 2
        assert tracker_warnings[0] == "Invalid Snowplow endpoint: notvalid:8080"
        assert tracker_warnings[1] == "Invalid Snowplow endpoint: file://bad.scheme"

        assert tracker.snowplow_tracker is not None
        assert len(tracker.snowplow_tracker.emitters) == 2

        emitter = tracker.snowplow_tracker.emitters[0]
        assert isinstance(emitter, Emitter)
        assert emitter.endpoint.startswith("https://valid.endpoint:8080/")

        emitter = tracker.snowplow_tracker.emitters[1]
        assert isinstance(emitter, Emitter)
        assert emitter.endpoint.startswith("https://other.endpoint/path/to/collector/")

    def test_client_id_from_env_var(
        self,
        project: Project,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        with delete_analytics_json(project):
            monkeypatch.setenv("MELTANO_CLIENT_ID", "invalid-context-uuid")
            with pytest.warns(RuntimeWarning, match="Invalid telemetry client UUID"):
                # Ensure it generated a random UUID as a fallback
                uuid.UUID(str(Tracker(project).client_id))

            ctx_id = new_client_id()
            monkeypatch.setenv("MELTANO_CLIENT_ID", str(ctx_id))
            # Ensure it takes the client ID from the env var
            assert Tracker(project).client_id == ctx_id

            monkeypatch.delenv("MELTANO_CLIENT_ID")
            # Ensure it uses the client ID stored in `analytics.json`
            assert Tracker(project).client_id == ctx_id

            ctx_id_2 = new_client_id()
            monkeypatch.setenv("MELTANO_CLIENT_ID", str(ctx_id_2))
            # Ensure the env var takes priority over `analytics.json`
            assert Tracker(project).client_id == ctx_id_2

            monkeypatch.delenv("MELTANO_CLIENT_ID")
            # Ensure the new client ID overwrites the old one in `analytics.json`
            assert Tracker(project).client_id == ctx_id_2
