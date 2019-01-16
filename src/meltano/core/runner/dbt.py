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

    def run(self, dry_run=False, models=None):
        self.dbt_service.deps()

        if models is not None:
            models = models.replace("-", "_")

        if dry_run:
            self.dbt_service.compile(models)
        else:
            self.dbt_service.run(models)
