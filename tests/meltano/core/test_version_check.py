"""Tests for the version check service."""

from __future__ import annotations

import json
import typing as t
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from unittest import mock

import pytest
import responses

from meltano.core.project import Project
from meltano.core.version_check import (
    CACHE_DURATION,
    PYPI_URL,
    VersionCheckResult,
    VersionCheckService,
)

if t.TYPE_CHECKING:
    from pathlib import Path


class TestVersionCheckService:
    """Test the VersionCheckService class."""

    @pytest.fixture(autouse=True)
    def not_editable(self):
        """Mock the installation to appear as if it is not editable."""
        with mock.patch(
            "meltano.core.version_check.editable_installation",
            return_value=None,
        ):
            yield

    @pytest.fixture
    def version_service(self, tmp_path: Path) -> VersionCheckService:
        """Create a VersionCheckService instance for testing."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        return VersionCheckService(cache_dir=cache_dir)

    def test_should_check_version_environment_variable(
        self,
        version_service: VersionCheckService,
        monkeypatch: pytest.MonkeyPatch,
    ):
        """Test that environment variable disables version check."""
        # Test various truthy values
        for value in ["1", "true", "yes", "True", "YES"]:
            monkeypatch.setenv("MELTANO_CLI_DISABLE_VERSION_CHECK", value)
            assert not version_service.should_check_version()

        # Test falsy values
        for value in ["0", "false", "no", ""]:
            monkeypatch.setenv("MELTANO_CLI_DISABLE_VERSION_CHECK", value)
            assert version_service.should_check_version()

        # Test when env var is not set
        monkeypatch.delenv("MELTANO_CLI_DISABLE_VERSION_CHECK", raising=False)
        assert version_service.should_check_version()

    def test_should_check_version_project_setting(self, tmp_path: Path):
        """Test that project setting disables version check."""
        project = mock.Mock(spec=Project)
        project.settings.get.return_value = False

        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        version_service = VersionCheckService(
            project=project,
            cache_dir=cache_dir,
        )

        # Setting is False (check enabled)
        project.settings.get.return_value = False
        assert version_service.should_check_version()

        # Setting is True (check disabled)
        project.settings.get.return_value = True
        assert not version_service.should_check_version()

    def test_is_development_version(self, version_service: VersionCheckService):
        """Test detection of development versions."""
        assert version_service._is_development_version("0.0.0")
        assert version_service._is_development_version("3.8.0.dev0")
        assert version_service._is_development_version("3.8.0dev123")
        assert not version_service._is_development_version("3.8.0")
        assert not version_service._is_development_version("3.8.0rc1")

    @responses.activate
    def test_fetch_latest_version_success(self, version_service: VersionCheckService):
        """Test successful fetching of latest version from PyPI."""
        pypi_response = {
            "info": {
                "version": "3.9.0",
                "name": "meltano",
            }
        }
        responses.add(responses.GET, PYPI_URL, json=pypi_response, status=HTTPStatus.OK)

        latest_version = version_service._fetch_latest_version()
        assert latest_version == "3.9.0"

    def test_cache_operations(self, version_service: VersionCheckService):
        """Test cache save and load operations."""
        # Test saving cache
        version_service._save_cache("3.9.0")

        # Test loading valid cache
        cache_data = version_service._load_cache()
        assert cache_data is not None
        assert cache_data["latest_version"] == "3.9.0"
        assert "check_timestamp" in cache_data

        # Test cache expiration
        # Manually modify cache to be expired
        cache_file = version_service._cache_file
        old_timestamp = (
            datetime.now(timezone.utc) - CACHE_DURATION - timedelta(minutes=1)
        )
        expired_cache = {
            "latest_version": "3.8.0",
            "check_timestamp": old_timestamp.isoformat(),
        }
        assert cache_file is not None
        with cache_file.open("w") as f:
            json.dump(expired_cache, f)

        # Should return None for expired cache
        cache_data = version_service._load_cache()
        assert cache_data is None

    @responses.activate
    def test_check_version_outdated(self, version_service: VersionCheckService) -> None:
        """Test version check when current version is outdated."""
        pypi_response = {
            "info": {
                "version": "3.9.0",
                "name": "meltano",
            }
        }
        responses.add(responses.GET, PYPI_URL, json=pypi_response, status=HTTPStatus.OK)

        with mock.patch(
            "meltano.core.version_check.importlib.metadata.version",
            return_value="3.7.0",
        ):
            result = version_service.check_version()

        assert result is not None
        assert isinstance(result, VersionCheckResult)
        assert result.current_version == "3.7.0"
        assert result.latest_version == "3.9.0"
        assert result.is_outdated
        assert result.upgrade_command is None

    @responses.activate
    def test_check_version_fetch_latest_version_failure(
        self,
        version_service: VersionCheckService,
    ) -> None:
        """Test handling of PyPI API failure."""
        responses.add(responses.GET, PYPI_URL, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        assert version_service.check_version() is None

    def test_check_version_invalid_version(
        self,
        version_service: VersionCheckService,
    ) -> None:
        """Test version check when current version is invalid."""
        with mock.patch(
            "meltano.core.version_check.importlib.metadata.version",
            return_value="invalid",
        ):
            result = version_service.check_version()

        assert result is None

    @responses.activate
    def test_check_version_up_to_date(
        self,
        version_service: VersionCheckService,
    ) -> None:
        """Test version check when current version is up to date."""
        pypi_response = {
            "info": {
                "version": "3.9.0",
                "name": "meltano",
            }
        }
        responses.add(responses.GET, PYPI_URL, json=pypi_response, status=HTTPStatus.OK)

        with mock.patch(
            "meltano.core.version_check.importlib.metadata.version",
            return_value="3.9.0",
        ):
            result = version_service.check_version()

        assert result is not None
        assert result.current_version == "3.9.0"
        assert result.latest_version == "3.9.0"
        assert not result.is_outdated
        assert result.upgrade_command is None

    def test_check_version_disabled(
        self,
        version_service: VersionCheckService,
        monkeypatch: pytest.MonkeyPatch,
    ):
        """Test version check when disabled."""
        monkeypatch.setenv("MELTANO_CLI_DISABLE_VERSION_CHECK", "1")

        result = version_service.check_version()
        assert result is None

    def test_check_version_development(
        self,
        version_service: VersionCheckService,
    ):
        """Test version check skips development versions."""
        with mock.patch(
            "meltano.core.version_check.importlib.metadata.version",
            return_value="0.0.0",
        ):
            result = version_service.check_version()

        assert result is None

    @pytest.mark.parametrize(
        ("result", "expected_message"),
        (
            pytest.param(
                VersionCheckResult(
                    current_version="3.7.0",
                    latest_version="3.9.0",
                    is_outdated=True,
                ),
                (
                    "A new version of Meltano is available (v3.9.0) and you are "
                    "currently running v3.7.0. For more information, visit: https://docs.meltano.com/getting-started/installation."
                ),
                id="outdated",
            ),
            pytest.param(
                VersionCheckResult(
                    current_version="3.9.0",
                    latest_version="3.9.0",
                    is_outdated=False,
                ),
                "",
                id="up-to-date",
            ),
            pytest.param(
                VersionCheckResult(
                    current_version="3.7.0",
                    latest_version="3.9.0",
                    is_outdated=True,
                    upgrade_command="pip install --upgrade meltano",
                ),
                (
                    "A new version of Meltano is available (v3.9.0) and you are "
                    "currently running v3.7.0. To upgrade: "
                    "`pip install --upgrade meltano`. For more information, visit: https://docs.meltano.com/getting-started/installation."
                ),
                id="outdated-with-upgrade-command",
            ),
        ),
    )
    def test_format_update_message(
        self,
        version_service: VersionCheckService,
        result: VersionCheckResult,
        expected_message: str,
    ):
        """Test formatting of update message."""
        message = version_service.format_update_message(result)
        assert message == expected_message

    @responses.activate
    def test_check_version_uses_cache(
        self,
        version_service: VersionCheckService,
    ):
        """Test that version check uses cached data when available."""
        # First check - should hit PyPI
        pypi_response = {
            "info": {
                "version": "3.9.0",
                "name": "meltano",
            }
        }
        responses.add(responses.GET, PYPI_URL, json=pypi_response, status=HTTPStatus.OK)

        with mock.patch(
            "meltano.core.version_check.importlib.metadata.version",
            return_value="3.7.0",
        ):
            result1 = version_service.check_version()

        assert result1 is not None
        assert result1.latest_version == "3.9.0"
        assert len(responses.calls) == 1

        # Second check - should use cache
        with mock.patch(
            "meltano.core.version_check.importlib.metadata.version",
            return_value="3.7.0",
        ):
            result2 = version_service.check_version()

        assert result2 is not None
        assert result2.latest_version == "3.9.0"
        assert len(responses.calls) == 1  # No additional API call
