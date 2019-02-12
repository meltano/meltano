from meltano.core.project import Project
from meltano.api.workers import MeltanoBackgroundCompiler


# for now Meltano only works on :5000
# see https://gitlab.com/meltano/meltano/issues/375
bind = ["0.0.0.0:5000"]
project = Project.find()
compiler = MeltanoBackgroundCompiler(project)


def when_ready(server):
    compiler.start()


def on_exit(server):
    compiler.stop()
