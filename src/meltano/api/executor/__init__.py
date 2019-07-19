import asyncio
import datetime
import os

from flask_executor import Executor

from meltano.core.plugin import PluginRef, PluginType
from meltano.core.project import Project
from meltano.core.runner.dbt import DbtRunner
from meltano.core.runner.singer import SingerRunner

executor = Executor()  # TODO name this executor_elt, follow the security pattern
loop = asyncio.get_event_loop()
watcher = asyncio.get_child_watcher()


def setup_executor(app, project):
    executor.init_app(app)
    watcher = asyncio.get_child_watcher()


def run_elt(project: Project, schedule_payload: dict):
    job_id = f'job_{datetime.datetime.now().strftime("%Y%m%d-%H:%M:%S.%f")}'
    future = executor.submit(run, project, schedule_payload, job_id)
    return job_id


def run(project: Project, schedule_payload: dict, job_id: str):
    extractor = schedule_payload["extractor"]
    loader = schedule_payload["loader"]
    transform = schedule_payload.get("transform")

    # TODO put in executor module (job_id , in singer runner for polling/query example)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    singer_runner = SingerRunner(
        project,
        job_id=job_id,
        run_dir=os.getenv("SINGER_RUN_DIR", project.meltano_dir("run")),
        target_config_dir=project.meltano_dir(PluginType.LOADERS, loader),
        tap_config_dir=project.meltano_dir(PluginType.EXTRACTORS, extractor),
    )

    try:
        if transform == "run" or transform == "skip":
            singer_runner.run(extractor, loader)
        if transform == "run":
            dbt_runner = DbtRunner(project)
            dbt_runner.run(extractor, loader, models=extractor)
    except Exception as err:
        raise Exception("ELT could not complete, an error happened during the process.")
