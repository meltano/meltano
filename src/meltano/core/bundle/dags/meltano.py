from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

from meltano.core.project import Project
project = Project.find()


default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime(2015, 6, 1),
        'email': ['airflow@example.com'],
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
        # 'queue': 'bash_queue',
        # 'pool': 'backfill',
        # 'priority_weight': 10,
        # 'end_date': datetime(2016, 1, 1),
        }

dag = DAG(
    'meltano',
    default_args=default_args,
    schedule_interval='@daily'
)

# t1, t2 and t3 are examples of tasks created by instantiating operators
t1 = BashOperator(
        task_id='extract_load',
        bash_command=f"cd {str(project.root)} && meltano elt tap-carbon-intensity target-sqlite --transform=skip",
        dag=dag)
