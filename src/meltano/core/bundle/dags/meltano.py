from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

from meltano.core.schedule_service import ScheduleService

import os

print("\n==== CWD ====")
print(os.getcwd())

import sys

print("\n==== sys.path ====")
print(sys.path)

print("\n==== PATH ====")
print(os.environ["PATH"])

from meltano.core.project import Project

project = Project.find()


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2015, 6, 1),
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

schedule_service = ScheduleService(project)

for schedule in schedule_service.schedules():
    dag_id = f"meltano_{schedule.name}"
    dag = DAG(dag_id, default_args=default_args, schedule_interval=schedule.interval)

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
