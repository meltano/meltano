import os
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, time, timedelta, MINYEAR

from meltano.core.schedule_service import ScheduleService
from meltano.core.project import Project
from meltano.core.utils import coerce_datetime


project = Project.find()

# I really don't like sending None here because it
# totally breaks the encapsulation. We should uncouple
# `Session` from the service.
schedule_service = ScheduleService(None, project)

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "concurrency": 1,
}

for schedule in schedule_service.schedules():
    catchup = False
    args = default_args.copy()

    if schedule.start_date:
        args["start_date"] = coerce_datetime(schedule.start_date)
        catchup = True

    dag_id = f"meltano_{schedule.name}"
    dag = DAG(
        dag_id, default_args=args, schedule_interval=schedule.interval, catchup=catchup
    )

    elt = BashOperator(
        task_id="extract_load",
        bash_command=f"echo $PATH; echo $VIRTUAL_ENV; cd {str(project.root)} && meltano elt {schedule.extractor} {schedule.loader} --transform={schedule.transform}",
        dag=dag,
        env={
            # inherit the current env
            **os.environ,
            **schedule.env,
        },
    )

    # register the dag
    globals()[dag_id] = dag
