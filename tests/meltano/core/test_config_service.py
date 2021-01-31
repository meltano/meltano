import os
import shutil

import pytest
import yaml


class TestConfigService:
    @pytest.fixture
    def subject(self, config_service):
        return config_service

    def test_default_init_should_not_fail(self, subject):
        assert subject
