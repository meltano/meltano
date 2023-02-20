from __future__ import annotations

import pytest

from meltano.cloud.api.config import MeltanoCloudConfig


class TestMeltanoCloudConfig:
    @pytest.fixture
    def subject(self):
        return MeltanoCloudConfig()

    def test_singleton(self, subject):
        assert subject is MeltanoCloudConfig()
