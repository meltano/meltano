"""Tests for manifest context managers."""

from __future__ import annotations

import os
import typing as t
from concurrent.futures import ThreadPoolExecutor
from contextvars import copy_context

import pytest

from meltano.core.manifest import Manifest
from meltano.core.manifest.contexts import (
    get_active_manifest_with_env,
    job_context,
    manifest_context,
    plugin_context,
    schedule_context,
)

if t.TYPE_CHECKING:
    from pathlib import Path

    from meltano.core.project import Project


@pytest.fixture
def mock_manifest(project: Project, tmp_path: Path) -> Manifest:
    """Create a mock manifest with test data."""
    manifest_data = {
        "version": 1,
        "project": str(project.root),
        "env": {
            "MANIFEST_VAR": "manifest_value",
            "OVERRIDE_ME": "manifest_override",
            "EXPANDABLE": "${BASE_VAR}_expanded",
        },
        "plugins": {
            "extractors": [
                {
                    "name": "tap-test",
                    "env": {
                        "TAP_TEST_API_KEY": "test_key",
                        "OVERRIDE_ME": "tap_override",
                        "TAP_EXPANDABLE": "${MANIFEST_VAR}_tap",
                    },
                }
            ],
            "loaders": [
                {
                    "name": "target-test",
                    "env": {
                        "TARGET_TEST_HOST": "localhost",
                        "OVERRIDE_ME": "target_override",
                    },
                }
            ],
        },
        "schedules": [
            {
                "name": "daily-sync",
                "env": {
                    "SCHEDULE_VAR": "schedule_value",
                    "OVERRIDE_ME": "schedule_override",
                },
            }
        ],
        "jobs": [
            {
                "name": "sync-job",
                "env": {
                    "JOB_VAR": "job_value",
                    "OVERRIDE_ME": "job_override",
                    "JOB_EXPANDABLE": "${SCHEDULE_VAR}_job",
                },
            }
        ],
    }

    manifest_path = tmp_path / "test-manifest.json"
    manifest = Manifest(
        project=project,
        path=manifest_path,
        check_schema=False,
        redact_secrets=False,
    )
    # Manually set the data since we're not loading from file
    manifest.data = manifest_data
    return manifest


class TestManifestContext:
    """Test manifest_context manager."""

    def test_manifest_context_basic(self, mock_manifest: Manifest) -> None:
        """Test basic manifest context functionality."""
        # Set a base variable for expansion
        os.environ["BASE_VAR"] = "base"

        # Ensure variables don't exist before context
        assert os.environ.get("MANIFEST_VAR") is None
        assert os.environ.get("OVERRIDE_ME") != "manifest_override"

        with manifest_context(mock_manifest):
            # Variables should be set within context
            assert os.environ["MANIFEST_VAR"] == "manifest_value"
            assert os.environ["OVERRIDE_ME"] == "manifest_override"
            assert os.environ["EXPANDABLE"] == "base_expanded"

        # Variables should be removed after context
        assert os.environ.get("MANIFEST_VAR") is None
        assert os.environ.get("OVERRIDE_ME") != "manifest_override"
        assert os.environ.get("EXPANDABLE") is None

    def test_manifest_context_preserves_existing(self, mock_manifest: Manifest) -> None:
        """Test that manifest context preserves existing env vars."""
        # Set existing values
        os.environ["OVERRIDE_ME"] = "original_value"
        os.environ["PRESERVE_ME"] = "keep_this"

        with manifest_context(mock_manifest):
            # Should override existing
            assert os.environ["OVERRIDE_ME"] == "manifest_override"
            # Should preserve unrelated vars
            assert os.environ["PRESERVE_ME"] == "keep_this"

        # Should restore original value
        assert os.environ["OVERRIDE_ME"] == "original_value"
        assert os.environ["PRESERVE_ME"] == "keep_this"

    def test_get_active_manifest_with_env(self, mock_manifest: Manifest) -> None:
        """Test getting active manifest with expanded env vars."""
        os.environ["BASE_VAR"] = "base"

        # No active manifest
        assert get_active_manifest_with_env() is None

        with manifest_context(mock_manifest):
            result = get_active_manifest_with_env()
            assert result is not None
            assert result["env"]["MANIFEST_VAR"] == "manifest_value"
            assert result["env"]["EXPANDABLE"] == "base_expanded"


class TestPluginContext:
    """Test plugin_context manager."""

    def test_plugin_context_basic(self, mock_manifest: Manifest) -> None:
        """Test basic plugin context functionality."""
        with manifest_context(mock_manifest):
            # Manifest vars should be set
            assert os.environ["MANIFEST_VAR"] == "manifest_value"

            with plugin_context("tap-test"):
                # Plugin vars should be set
                assert os.environ["TAP_TEST_API_KEY"] == "test_key"
                # Plugin should override manifest
                assert os.environ["OVERRIDE_ME"] == "tap_override"
                # Expansion should work with manifest vars
                assert os.environ["TAP_EXPANDABLE"] == "manifest_value_tap"

            # Plugin vars should be removed
            assert os.environ.get("TAP_TEST_API_KEY") is None
            assert os.environ["OVERRIDE_ME"] == "manifest_override"

    def test_plugin_context_without_manifest(self) -> None:
        """Test plugin context without active manifest."""
        with plugin_context("tap-test"):
            # Should not fail, but won't set any env vars
            pass

    def test_plugin_context_unknown_plugin(self, mock_manifest: Manifest) -> None:
        """Test plugin context with unknown plugin."""
        with manifest_context(mock_manifest), plugin_context("tap-unknown"):
            # Should not fail, but won't set plugin-specific vars
            assert os.environ["MANIFEST_VAR"] == "manifest_value"


class TestScheduleContext:
    """Test schedule_context manager."""

    def test_schedule_context_basic(self, mock_manifest: Manifest) -> None:
        """Test basic schedule context functionality."""
        with manifest_context(mock_manifest):
            with schedule_context("daily-sync"):
                assert os.environ["SCHEDULE_VAR"] == "schedule_value"
                assert os.environ["OVERRIDE_ME"] == "schedule_override"

            assert os.environ.get("SCHEDULE_VAR") is None
            assert os.environ["OVERRIDE_ME"] == "manifest_override"

    def test_schedule_context_without_manifest(self) -> None:
        """Test schedule context without active manifest."""
        with schedule_context("daily-sync"):
            # Should not fail
            pass


class TestJobContext:
    """Test job_context manager."""

    def test_job_context_basic(self, mock_manifest: Manifest) -> None:
        """Test basic job context functionality."""
        with (
            manifest_context(mock_manifest),
            schedule_context("daily-sync"),
            job_context("sync-job"),
        ):
            assert os.environ["JOB_VAR"] == "job_value"
            assert os.environ["OVERRIDE_ME"] == "job_override"
            # Should have access to schedule vars for expansion
            assert os.environ["JOB_EXPANDABLE"] == "schedule_value_job"

    def test_job_context_without_manifest(self) -> None:
        """Test job context without active manifest."""
        with job_context("sync-job"):
            # Should not fail
            pass


class TestContextNesting:
    """Test nested context behavior."""

    def test_full_context_hierarchy(self, mock_manifest: Manifest) -> None:
        """Test full hierarchy: manifest -> plugin -> schedule -> job."""
        os.environ["BASE_VAR"] = "base"
        original_override = os.environ.get("OVERRIDE_ME", "none")

        with manifest_context(mock_manifest):
            assert os.environ["OVERRIDE_ME"] == "manifest_override"

            with plugin_context("tap-test"):
                assert os.environ["OVERRIDE_ME"] == "tap_override"

                with schedule_context("daily-sync"):
                    assert os.environ["OVERRIDE_ME"] == "schedule_override"

                    with job_context("sync-job"):
                        # Job should win in precedence
                        assert os.environ["OVERRIDE_ME"] == "job_override"

                        # All vars should be accessible
                        assert os.environ["MANIFEST_VAR"] == "manifest_value"
                        assert os.environ["TAP_TEST_API_KEY"] == "test_key"
                        assert os.environ["SCHEDULE_VAR"] == "schedule_value"
                        assert os.environ["JOB_VAR"] == "job_value"

                    # Should revert to schedule
                    assert os.environ["OVERRIDE_ME"] == "schedule_override"
                    assert os.environ.get("JOB_VAR") is None

                # Should revert to plugin
                assert os.environ["OVERRIDE_ME"] == "tap_override"
                assert os.environ.get("SCHEDULE_VAR") is None

            # Should revert to manifest
            assert os.environ["OVERRIDE_ME"] == "manifest_override"
            assert os.environ.get("TAP_TEST_API_KEY") is None

        # Should revert to original
        if original_override == "none":
            assert os.environ.get("OVERRIDE_ME") is None
        else:
            assert os.environ["OVERRIDE_ME"] == original_override


class TestContextVarsIsolation:
    """Test contextvars isolation between concurrent executions."""

    def test_concurrent_manifest_contexts(
        self, project: Project, tmp_path: Path
    ) -> None:
        """Test that concurrent contexts are isolated."""

        def create_manifest(name: str, value: str) -> Manifest:
            manifest = Manifest(
                project=project,
                path=tmp_path / f"{name}.json",
                check_schema=False,
                redact_secrets=False,
            )
            manifest.data = {
                "version": 1,
                "project": str(project.root),
                "env": {f"{name}_VAR": value},
            }
            return manifest

        manifest1 = create_manifest("MANIFEST1", "value1")
        manifest2 = create_manifest("MANIFEST2", "value2")

        results = []

        def run_in_context(
            manifest: Manifest, expected_var: str, expected_val: str
        ) -> None:
            with manifest_context(manifest):
                # Verify our var is set
                assert os.environ.get(expected_var) == expected_val
                # Verify we can get the active manifest
                active = get_active_manifest_with_env()
                assert active is not None
                assert active["env"][expected_var] == expected_val
                results.append((expected_var, expected_val))

        # Run contexts in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Each runs in its own context (contextvars are thread-local)
            ctx1 = copy_context()
            ctx2 = copy_context()

            future1 = executor.submit(
                ctx1.run,
                run_in_context,
                manifest1,
                "MANIFEST1_VAR",
                "value1",
            )
            future2 = executor.submit(
                ctx2.run,
                run_in_context,
                manifest2,
                "MANIFEST2_VAR",
                "value2",
            )

            future1.result()
            future2.result()

        # Both should have completed successfully
        assert len(results) == 2
        assert ("MANIFEST1_VAR", "value1") in results
        assert ("MANIFEST2_VAR", "value2") in results


class TestEnvVarExpansion:
    """Test environment variable expansion in contexts."""

    def test_expansion_order(self, mock_manifest: Manifest) -> None:
        """Test that env vars are expanded in the correct order."""
        # Set up a chain of expansions
        manifest_data = {
            "version": 1,
            "project": str(mock_manifest.project.root),
            "env": {
                "A": "a",
                "B": "${A}b",
                "C": "${B}c",
            },
            "plugins": {
                "extractors": [
                    {
                        "name": "tap-test",
                        "env": {
                            "D": "${C}d",
                            "E": "${D}e",
                        },
                    }
                ],
            },
        }
        mock_manifest.data = manifest_data

        with manifest_context(mock_manifest):
            assert os.environ["A"] == "a"
            assert os.environ["B"] == "ab"
            assert os.environ["C"] == "abc"

            with plugin_context("tap-test"):
                assert os.environ["D"] == "abcd"
                assert os.environ["E"] == "abcde"

    def test_circular_expansion(self, mock_manifest: Manifest) -> None:
        """Test that circular references don't cause infinite loops."""
        manifest_data = {
            "version": 1,
            "project": str(mock_manifest.project.root),
            "env": {
                "A": "${B}",
                "B": "${A}",
            },
        }
        mock_manifest.data = manifest_data

        with manifest_context(mock_manifest):
            # Should handle circular refs gracefully
            # The exact behavior depends on expand_env_vars implementation
            assert "A" in os.environ
            assert "B" in os.environ
