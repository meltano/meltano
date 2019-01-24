from meltano.core.project import Project
from meltano.api.workers import MeltanoBackgroundCompiler


project = Project.find()
compiler = MeltanoBackgroundCompiler(project)


def when_ready(server):
    compiler.start()


def on_exit(server):
    compiler.stop()
