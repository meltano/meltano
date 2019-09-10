import logging
import os
from sqlalchemy import create_engine

import meltano.api.config as _config
from meltano.core.project import Project
from meltano.core.migration_service import MigrationService
from meltano.api.workers import MeltanoBackgroundCompiler, AirflowWorker


_port = os.getenv("MELTANO_API_PORT", "5000")
_host = os.getenv("MELTANO_API_HOSTNAME", "0.0.0.0")

bind = [f"{_host}:{_port}"]
project = Project.find()

_workers = []
_workers.append(MeltanoBackgroundCompiler(project))
try:
    _workers.append(AirflowWorker(project))
except:
    logging.info("Airflow is not installed.")


def when_ready(server):
    engine = create_engine(_config.SQLALCHEMY_DATABASE_URI)
    MigrationService(engine).upgrade()
    engine.dispose()

    for worker in _workers:
        worker.start()


def on_exit(server):
    for worker in _workers:
        worker.stop()
