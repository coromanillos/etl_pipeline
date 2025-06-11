import os
import yaml
from pathlib import Path
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.email import EmailOperator
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.trigger_rule import TriggerRule

# Load configuration from YAML
def load_config():
    config_path = Path("/app/config/config.yaml")
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    with config_path.open("r") as f:
        return yaml.safe_load(f)

config = load_config()

notification_recipients = config['notifications']['recipients']
alert_email_from = os.getenv("ALERT_FROM_EMAIL")

default_args = {
    'owner': 'airflow',
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def fail_task():
    raise ValueError("Simulated failure to test email alerting.")

with DAG(
    dag_id='email_alert_dag',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
    catchup=False,
    tags=['alerts', 'email'],
    description='Test DAG that sends email alerts on task failure using config.yaml'
) as dag:

    start = DummyOperator(task_id='start')

    simulate_failure = PythonOperator(
        task_id='simulate_failure',
        python_callable=fail_task
    )

    send_alert = EmailOperator(
        task_id='send_failure_alert',
        to=notification_recipients,
        subject='🚨 Airflow Alert: Task Failed - {{ task_instance.task_id }}',
        html_content="""
        <h3>Airflow Task Failed</h3>
        <p><strong>DAG:</strong> {{ dag.dag_id }}</p>
        <p><strong>Task:</strong> {{ task_instance.task_id }}</p>
        <p><strong>Execution Time:</strong> {{ execution_date }}</p>
        <p><strong>Log URL:</strong> <a href="{{ task_instance.log_url }}">{{ task_instance.log_url }}</a></p>
        """,
        from_email=alert_email_from,
        trigger_rule=TriggerRule.ONE_FAILED
    )

    end = DummyOperator(task_id='end')

    start >> simulate_failure >> send_alert >> end
