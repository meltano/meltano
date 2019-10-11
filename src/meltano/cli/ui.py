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
@project(migrate=True)
def ui(project, reload, bind_port, bind):
    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_ui()

    workers = []
    if not truthy(os.getenv("MELTANO_DISABLE_AIRFLOW", False)):
        workers.append(AirflowWorker(project))

    workers.append(MeltanoBackgroundCompiler(project))
    workers.append(UIAvailableWorker("http://localhost:{bind_port}"))
    workers.append(
        APIWorker(
            project,
            f"{bind}:{bind_port}",
            reload=reload or os.getenv("FLASK_ENV") == "development",
        )
    )

    cleanup = start_workers(workers)
    handle_terminate = lambda signal, frame: cleanup()
    signal.signal(signal.SIGTERM, handle_terminate)

    logger.info("All workers started.")
