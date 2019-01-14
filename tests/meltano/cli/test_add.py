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


def test_add_transformer(project):
    service = ProjectAddService(project)
    service.add(PluginType.TRANSFORMERS, "dbt")

    assert PluginType.TRANSFORMERS in project.meltano
    assert any(
        plugin["name"] == "dbt" for plugin in project.meltano[PluginType.TRANSFORMERS]
    )


def test_add_transform(project):
    service = ProjectAddService(project)
    service.add(PluginType.TRANSFORMS, "tap-carbon-intensity")

    assert PluginType.TRANSFORMS in project.meltano
    assert any(
        plugin["name"] == "tap-carbon-intensity" for plugin in project.meltano[PluginType.TRANSFORMS]
    )
