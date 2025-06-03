from airflow import DAG
from airflow.operators.dummy import DummyOperator
from datetime import datetime

with DAG("test_dag", start_date=datetime(2024, 1, 1), schedule_interval=None, catchup=False) as dag:
    DummyOperator(task_id="start")
