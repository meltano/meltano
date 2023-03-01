from __future__ import annotations

import pytest
from aioresponses import aioresponses
from click.testing import CliRunner

from meltano.cloud.api.auth import MeltanoCloudAuth
from meltano.cloud.cli import cloud as cli


class TestCloudLogin:
    """Test the Meltano Cloud login command."""

    @pytest.fixture
    def auth(self):
        return MeltanoCloudAuth()

    def test_login_success(
        self, monkeypatch: pytest.MonkeyPatch, auth: MeltanoCloudAuth
    ):
        monkeypatch.setenv("MELTANO_CLOUD_ORGANIZATION_ID", "meltano-cloud-test")
        # TODO
