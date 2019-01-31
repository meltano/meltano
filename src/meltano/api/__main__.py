# DEPRECATED: do we have any good reason to keep this
# method of booting the web ui?
# We now have the `meltano ui` command that
# should take care of this.
from meltano.api.app import start
from meltano.core.project import Project


start(Project.find(), host="0.0.0.0")
