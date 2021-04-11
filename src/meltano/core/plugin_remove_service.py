import shutil

from meltano.core.plugin.project_plugin import ProjectPlugin

from .project import Project


class PluginRemoveService:
    def __init__(self, project: Project):
        self.project = project

    def remove_plugin(
        self,
        plugin: ProjectPlugin,
    ):

        path = self.project.meltano_dir().joinpath(plugin.type, plugin.name)
        shutil.rmtree(path)
