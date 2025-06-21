# slack_alert_dag.py

import os
import yaml
from pathlib import Path
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from src.utils.default_args import default_args


# Load configuration from YAML
def load_config():
    config_path = Path("/app/config/config.yaml")
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    with config_path.open("r") as f:
        return yaml.safe_load(f)

config = load_config()

# This variable must be set in Airflow connections, not just in .env
# Go to Airflow UI → Admin → Connections → +Add
# Set Conn Id = 'slack_alerts'
# Set Conn Type = 'Slack Webhook'
# Set Host = value of SLACK_WEBHOOK_URL from .env
slack_conn_id = 'slack_alerts'

default_args = {
    'owner': 'airflow',
    'email_on_failure': False,  # Email is fully disabled now
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def fail_task():
    raise ValueError("Simulated failure to test Slack alerting.")

with DAG(
    dag_id='slack_alert_dag',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
    catchup=False,
    tags=['alerts', 'slack'],
    description='Test DAG that sends Slack alerts on task failure using SlackWebhookOperator'
) as dag:

    start = DummyOperator(task_id='start')

    simulate_failure = PythonOperator(
        task_id='simulate_failure',
        python_callable=fail_task
    )

    send_slack_alert = SlackWebhookOperator(
        task_id='send_failure_alert',
        http_conn_id=slack_conn_id,
        message="""
        :rotating_light: *Airflow Task Failed*
        *DAG:* {{ dag.dag_id }}
        *Task:* {{ task_instance.task_id }}
        *Execution Time:* {{ execution_date }}
        *Log URL:* <{{ task_instance.log_url }}|View Logs>
        """,
        trigger_rule=TriggerRule.ONE_FAILED
    )

    end = DummyOperator(task_id='end')

    start >> simulate_failure >> send_slack_alert >> end
