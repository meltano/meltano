import os
import subprocess
import click
import signal
import logging

from . import cli
from .params import project
from meltano.core.db import project_engine
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.utils import truthy
from meltano.core.migration_service import MigrationService
from meltano.api.workers import (
    airflow_context,
    MeltanoBackgroundCompiler,
    AirflowWorker,
    APIWorker,
    UIAvailableWorker,
)


logger = logging.getLogger(__name__)


def start_workers(workers):
    def stop_all():
        logger.info("Stopping all background workers...")
        for worker in workers:
            worker.stop()

    # start all workers
    for worker in workers:
        worker.start()

    return stop_all


@cli.command()
@click.option("--reload", is_flag=True, default=False)
@click.option(
    "--bind-port",
    default=5000,
    help="Port to run webserver on",
    envvar="MELTANO_API_PORT",
    type=int,
)
@click.option(
    "--bind",
    default="0.0.0.0",
    help="The hostname (or IP address) to bind on",
    envvar="MELTANO_API_HOSTNAME",
)
@project
def ui(project, reload, bind_port, bind):
    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_ui()

    engine, _ = project_engine(project)
    # TODO: move to `project_engine`
    os.environ["MELTANO_DATABASE_URI"] = str(engine.url)
    migration_service = MigrationService(engine)
    migration_service.upgrade()

    workers = []

    if not truthy(os.getenv("AIRFLOW_DISABLED", False)):
        # TODO: move to the class
        airflow_context["worker"] = AirflowWorker(project)
        workers.append(airflow_context["worker"])

    workers.append(MeltanoBackgroundCompiler(project))
    workers.append(UIAvailableWorker("http://localhost:{bind_port}"))
    workers.append(
        APIWorker(project, reload=reload or os.getenv("FLASK_ENV") == "development")
    )

    cleanup = start_workers(workers)
    handle_terminate = lambda signal, frame: cleanup()
    signal.signal(signal.SIGTERM, handle_terminate)

    logger.info("All workers started.")
