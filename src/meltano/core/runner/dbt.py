import logging
import subprocess
from io import StringIO

from . import Runner
from meltano.core.project import Project
from meltano.core.dbt_service import DbtService


class DbtRunner(Runner):
    def __init__(self, project: Project, dbt_service: DbtService = None):
        self.project = project
        self.dbt_service = dbt_service or DbtService(project)

    def run(self, dry_run=False):
        self.dbt_service.deps()

        if dry_run:
            self.dbt_service.compile()
        else:
            self.dbt_service.run()
