###################################################
# Title: rest_to_postgres.py
# Author: Christopher Romanillos
# Description: Moves weekly api data to postgres
# First phase of ETL
# Date: 06/26/25
###################################################

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import logging
import yaml

from src.etl_rest_to_postgres.extract import extract_data
from src.etl_rest_to_postgres.transform import process_raw_data
from src.etl_rest_to_postgres.postgres_loader import load_data
from src.utils.slack_alert import slack_failed_task_alert

logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    'owner': 'airflow',
    'depends_on_past': False,
    'on_failure_callback': slack_failed_task_alert,
    'retries': 1,
}

def load_config():
    with open("/opt/airflow/config/config.yaml") as f:
        return yaml.safe_load(f)

with DAG(
    dag_id="rest_to_postgres",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["etl", "alpha_vantage"],
) as dag:

    def extract_task(ti, **kwargs):
        config = load_config()
        logger.info("Starting extraction task.")
        data = extract_data(config)
        if not data:
            raise ValueError("Extraction failed.")
        ti.xcom_push(key='raw_data', value=data)

    # similar for transform_task and load_task but also load config inside

    extract = PythonOperator(task_id="extract", python_callable=extract_task)
    # similarly define transform and load tasks...

    extract >> transform >> load
