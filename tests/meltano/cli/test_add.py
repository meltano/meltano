import yaml

from meltano.core.project_add_service import ProjectAddService
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.plugin import PluginType


def test_add_extractor(project):
    # TODO: mock
    discovery_service = PluginDiscoveryService()

    service = ProjectAddService(
        project,
        plugin_type=PluginType.EXTRACTORS,
        plugin_name="tap-first",  # TODO: create tap-test
        discovery_service=discovery_service,
    )
    service.add()
    meltano_config = yaml.load(project.meltanofile.open())

    assert PluginType.EXTRACTORS in meltano_config
    assert any(
        plugin["name"] == "tap-first"
        for plugin in meltano_config[PluginType.EXTRACTORS]
    )


def test_add_loader(project):
    # TODO: mock
    discovery_service = PluginDiscoveryService()

    service = ProjectAddService(
        project,
        plugin_type=PluginType.LOADERS,
        plugin_name="target-csv",  # TODO: create target-test
        discovery_service=discovery_service,
    )
    service.add()

    meltano_config = yaml.load(project.meltanofile.open())

    assert PluginType.LOADERS in meltano_config
    assert any(
        plugin["name"] == "target-csv" for plugin in meltano_config[PluginType.LOADERS]
    )
