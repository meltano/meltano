import yaml

from meltano.core.project_add_service import ProjectAddService
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.plugin import PluginType


def test_add_extractor(project):
    service = ProjectAddService(project)
    service.add(PluginType.EXTRACTORS, "tap-gitlab")

    assert PluginType.EXTRACTORS in project.meltano
    assert any(
        plugin["name"] == "tap-gitlab"
        for plugin in project.meltano[PluginType.EXTRACTORS]
    )


def test_add_loader(project):
    service = ProjectAddService(project)
    service.add(PluginType.LOADERS, "target-csv")

    assert PluginType.LOADERS in project.meltano
    assert any(
        plugin["name"] == "target-csv" for plugin in project.meltano[PluginType.LOADERS]
    )
