"""Tests for the version check service."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

import pytest
import responses

from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.version_check import (
    CACHE_DURATION,
    PYPI_URL,
    VersionCheckResult,
    VersionCheckService,
)


class TestVersionCheckService:
    """Test the VersionCheckService class."""

    @pytest.fixture
    def version_service(self, tmp_path):
        """Create a VersionCheckService instance for testing."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        return VersionCheckService(cache_dir=cache_dir)

    @pytest.fixture
    def mock_settings_service(self):
        """Create a mock ProjectSettingsService."""
        mock_service = mock.Mock(spec=ProjectSettingsService)
        mock_service.get.return_value = False  # version check enabled by default
        return mock_service

    def test_should_check_version_environment_variable(self, version_service, monkeypatch):
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

    def test_should_check_version_project_setting(self, tmp_path, mock_settings_service):
        """Test that project setting disables version check."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        version_service = VersionCheckService(
            project_settings_service=mock_settings_service,
            cache_dir=cache_dir,
        )

        # Setting is False (check enabled)
        mock_settings_service.get.return_value = False
        assert version_service.should_check_version()

        # Setting is True (check disabled)
        mock_settings_service.get.return_value = True
        assert not version_service.should_check_version()

    def test_is_development_version(self, version_service):
        """Test detection of development versions."""
        assert version_service._is_development_version("0.0.0")
        assert version_service._is_development_version("3.8.0.dev0")
        assert version_service._is_development_version("3.8.0dev123")
        assert not version_service._is_development_version("3.8.0")
        assert not version_service._is_development_version("3.8.0rc1")

    @responses.activate
    def test_fetch_latest_version_success(self, version_service):
        """Test successful fetching of latest version from PyPI."""
        pypi_response = {
            "info": {
                "version": "3.9.0",
                "name": "meltano",
            }
        }
        responses.add(
            responses.GET,
            PYPI_URL,
            json=pypi_response,
            status=200,
        )

        latest_version = version_service._fetch_latest_version()
        assert latest_version == "3.9.0"

    @responses.activate
    def test_fetch_latest_version_failure(self, version_service):
        """Test handling of PyPI API failure."""
        responses.add(
            responses.GET,
            PYPI_URL,
            status=500,
        )

        latest_version = version_service._fetch_latest_version()
        assert latest_version is None

    def test_cache_operations(self, version_service):
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
        old_timestamp = datetime.now(timezone.utc) - CACHE_DURATION - timedelta(minutes=1)
        expired_cache = {
            "latest_version": "3.8.0",
            "check_timestamp": old_timestamp.isoformat(),
        }
        with open(cache_file, "w") as f:
            json.dump(expired_cache, f)

        # Should return None for expired cache
        cache_data = version_service._load_cache()
        assert cache_data is None

    def test_get_upgrade_command(self, version_service, monkeypatch):
        """Test detection of appropriate upgrade command."""
        # Test default (pip)
        command = version_service._get_upgrade_command()
        assert "pip install" in command

        # Test with uv installed
        def mock_exists_uv(self):
            return self.name == "uv"

        with mock.patch("pathlib.Path.exists", mock_exists_uv):
            command = version_service._get_upgrade_command()
            assert command == "uv pip install --upgrade meltano"

        # Test pipx detection
        monkeypatch.setenv("PIPX_HOME", str(Path.home() / ".local/pipx"))
        
        def mock_exists_pipx(self):
            # Mock pipx home directory to exist
            return str(self) == str(Path.home() / ".local/pipx")

        # Mock sys.executable to be in a pipx path
        with mock.patch("sys.executable", str(Path.home() / ".local/pipx/venvs/meltano/bin/python")):
            with mock.patch("pathlib.Path.exists", mock_exists_pipx):
                command = version_service._get_upgrade_command()
                assert command == "pipx upgrade meltano"

    @responses.activate
    def test_check_version_outdated(self, version_service, monkeypatch):
        """Test version check when current version is outdated."""
        monkeypatch.setattr("meltano.core.version_check.__version__", "3.7.0")
        
        pypi_response = {
            "info": {
                "version": "3.9.0",
                "name": "meltano",
            }
        }
        responses.add(
            responses.GET,
            PYPI_URL,
            json=pypi_response,
            status=200,
        )

        result = version_service.check_version()
        assert result is not None
        assert isinstance(result, VersionCheckResult)
        assert result.current_version == "3.7.0"
        assert result.latest_version == "3.9.0"
        assert result.is_outdated
        assert result.upgrade_command is not None

    @responses.activate
    def test_check_version_up_to_date(self, version_service, monkeypatch):
        """Test version check when current version is up to date."""
        monkeypatch.setattr("meltano.core.version_check.__version__", "3.9.0")
        
        pypi_response = {
            "info": {
                "version": "3.9.0",
                "name": "meltano",
            }
        }
        responses.add(
            responses.GET,
            PYPI_URL,
            json=pypi_response,
            status=200,
        )

        result = version_service.check_version()
        assert result is not None
        assert result.current_version == "3.9.0"
        assert result.latest_version == "3.9.0"
        assert not result.is_outdated
        assert result.upgrade_command is None

    def test_check_version_disabled(self, version_service, monkeypatch):
        """Test version check when disabled."""
        monkeypatch.setenv("MELTANO_CLI_DISABLE_VERSION_CHECK", "1")
        
        result = version_service.check_version()
        assert result is None

    def test_check_version_development(self, version_service, monkeypatch):
        """Test version check skips development versions."""
        monkeypatch.setattr("meltano.core.version_check.__version__", "0.0.0")
        
        result = version_service.check_version()
        assert result is None

    def test_format_update_message(self, version_service):
        """Test formatting of update message."""
        result = VersionCheckResult(
            current_version="3.7.0",
            latest_version="3.9.0",
            is_outdated=True,
            upgrade_command="pip install --upgrade meltano",
        )

        message = version_service.format_update_message(result)
        assert "A new version of Meltano is available (v3.9.0)!" in message
        assert "You are currently running v3.7.0." in message
        assert "pip install --upgrade meltano" in message
        assert "https://docs.meltano.com/guide/installation" in message

        # Test no message for up-to-date version
        result_up_to_date = VersionCheckResult(
            current_version="3.9.0",
            latest_version="3.9.0",
            is_outdated=False,
        )
        message = version_service.format_update_message(result_up_to_date)
        assert message == ""

    @responses.activate
    def test_check_version_uses_cache(self, version_service, monkeypatch):
        """Test that version check uses cached data when available."""
        monkeypatch.setattr("meltano.core.version_check.__version__", "3.7.0")
        
        # First check - should hit PyPI
        pypi_response = {
            "info": {
                "version": "3.9.0",
                "name": "meltano",
            }
        }
        responses.add(
            responses.GET,
            PYPI_URL,
            json=pypi_response,
            status=200,
        )

        result1 = version_service.check_version()
        assert result1.latest_version == "3.9.0"
        assert len(responses.calls) == 1

        # Second check - should use cache
        result2 = version_service.check_version()
        assert result2.latest_version == "3.9.0"
        assert len(responses.calls) == 1  # No additional API call