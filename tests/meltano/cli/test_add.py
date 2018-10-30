import yaml

from meltano.core.project_add_service import ProjectAddService
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.plugin import PluginType


def test_add_extractor(project):
    service = ProjectAddService(project)
    service.add(PluginType.EXTRACTORS, "tap-first")
    meltano_config = yaml.load(project.meltanofile.open())

    assert PluginType.EXTRACTORS in meltano_config
    assert any(
        plugin["name"] == "tap-first"
        for plugin in meltano_config[PluginType.EXTRACTORS]
    )


def test_add_loader(project):
    service = ProjectAddService(project)
    service.add(PluginType.LOADERS, "target-csv")

    meltano_config = yaml.load(project.meltanofile.open())

    assert PluginType.LOADERS in meltano_config
    assert any(
        plugin["name"] == "target-csv" for plugin in meltano_config[PluginType.LOADERS]
    )
