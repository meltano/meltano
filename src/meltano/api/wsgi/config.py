import logging
from meltano.core.project import Project
from meltano.api.workers import MeltanoBackgroundCompiler, AirflowWorker


# for now Meltano only works on :5000
# see https://gitlab.com/meltano/meltano/issues/375
bind = ["0.0.0.0:5000"]
project = Project.find()

_workers = []
_workers.append(MeltanoBackgroundCompiler(project))
try:
    _workers.append(AirflowWorker(project))
except:
    logging.info("Airflow is not installed.")


def when_ready(server):
    for worker in _workers:
        worker.start()


def on_exit(server):
    for worker in _workers:
        worker.stop()
