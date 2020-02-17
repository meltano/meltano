import pytest
import yaml
import os
import shutil

from meltano.core.config_service import ConfigService
from meltano.core.plugin import Plugin, PluginType


class TestConfigService:
    @pytest.fixture
    def subject(self, config_service):
        return config_service

    def test_default_init_should_not_fail(self, subject):
        assert subject

    def test_get_plugin(self, subject, tap):
        assert subject.get_plugin(tap).type == PluginType.EXTRACTORS

    def test_update_plugin(self, subject, tap):
        # update a tap with a random value
        tap.config["test"] = 42
        outdated = subject.update_plugin(tap)
        assert subject.get_plugin(tap).config["test"] == 42

        # revert back
        subject.update_plugin(outdated)
        assert subject.get_plugin(tap).config == {}

    def test_get_extractors(self, subject, tap):
        extractors = list(subject.get_extractors())
        assert len(extractors) == 1
        assert all(map(lambda p: p.type == PluginType.EXTRACTORS, extractors))

    def test_get_loaders(self, subject, target):
        loaders = list(subject.get_loaders())
        assert len(loaders) == 1
        assert all(map(lambda p: p.type == PluginType.LOADERS, loaders))
