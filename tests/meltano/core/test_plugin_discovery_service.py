import pytest
import requests_mock
import json
from unittest import mock

from meltano.core.plugin import PluginType
from meltano.core.plugin_discovery_service import PluginDiscoveryService, MELTANO_DISCOVERY_URL
from meltano.core.behavior.versioned import IncompatibleVersionError


class TestPluginDiscoveryService:
    @pytest.fixture
    def subject(self, plugin_discovery_service):
        return plugin_discovery_service

    @pytest.fixture
    def extraneous_plugin(self, subject):
        subject.discovery["turboencabulators"] = [{"name": "v1", "config": None}]

    @pytest.fixture
    def discovery_yaml(self, subject):
        """Disable the discovery mock"""
        subject._discovery = None

    def test_plugins(self, subject):
        plugins = list(subject.plugins())

        assert subject.discovery
        assert len(plugins) == 6

    @pytest.mark.usefixtures("extraneous_plugin")
    def test_plugins_unknown(self, subject):
        plugins = list(subject.plugins())
        assert len(plugins) == 6

    def test_discovery(self, subject):
        # test for a specific plugin type
        discovery = subject.discover(PluginType.EXTRACTORS)
        assert PluginType.EXTRACTORS in discovery
        assert PluginType.LOADERS not in discovery

        # test for all
        discovery = subject.discover(PluginType.ALL)
        for t in PluginType:
            if t is PluginType.ALL:
                continue

            assert t in discovery
            assert isinstance(discovery[t], list)

    @pytest.mark.usefixtures("discovery_yaml")
    def test_discovery_yaml(self, subject):
        # test for all
        discovery = subject.discover(PluginType.ALL)

        # raw yaml load
        for plugin_type, plugin_defs in subject._discovery.items():
            if plugin_type == "version":
                continue

            plugin_type = PluginType(plugin_type)
            plugin_names = [
                plugin["name"]
                for plugin in sorted(plugin_defs, key=lambda k: k["name"])
            ]

            assert plugin_type in discovery
            assert discovery[plugin_type] == plugin_names

    @pytest.mark.usefixtures("extraneous_plugin")
    def test_discovery_unknown(self, subject):
        # test for all
        discovery = subject.discover(PluginType.ALL)

        for t in PluginType:
            if t is PluginType.ALL:
                continue

            assert t in discovery
            assert isinstance(discovery[t], list)
            assert "turboencabulator" not in discovery

    def test_cached_discovery(self, subject):
        # fmt: off
        with mock.patch.object(PluginDiscoveryService, "cached_discovery",
                               new_callable=mock.PropertyMock,
                               return_value=subject._discovery) as cached_discovery, \
            requests_mock.Mocker() as r:
        # fmt: on
            r.get(MELTANO_DISCOVERY_URL, status_code=500)
            discovery = subject.fetch_discovery()

            assert cached_discovery.called

        assert discovery == subject._discovery


class TestIncompatiblePluginDiscoveryService:
    @pytest.fixture
    def subject(self, plugin_discovery_service):
        return plugin_discovery_service

    @pytest.fixture
    def discovery_yaml(self, subject):
        subject._discovery['version'] = 1000

    @pytest.mark.usefixtures("discovery_yaml")
    def test_discovery(self, subject):
        with pytest.raises(IncompatibleVersionError):
            subject.ensure_compatible()

    @pytest.mark.usefixtures("discovery_yaml")
    def test_remote_incompatible(self, subject):
        compatible_discovery = subject._discovery.copy()
        compatible_discovery["version"] = PluginDiscoveryService.__version__

        # fmt: off
        with mock.patch.object(PluginDiscoveryService, "cached_discovery",
                               new_callable=mock.PropertyMock,
                               return_value=compatible_discovery) as cached_discovery, \
            requests_mock.Mocker() as r:
        # fmt: on
            r.get(MELTANO_DISCOVERY_URL, text=json.dumps(subject._discovery))
            subject.fetch_discovery()

            assert cached_discovery.called
