###################################################
# Title: rest_to_postgres.py
# Author: Christopher Romanillos
# Description: Moves weekly API data to PostgreSQL
# First phase of ETL (extract-transform-load)
# Date: 2025-07-05 | Version: 2.1 (testable, refactored)
###################################################

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import logging

from src.etl_rest_to_postgres.extract import extract_data
from src.etl_rest_to_postgres.transform import process_raw_data
from src.etl_rest_to_postgres.postgres_loader import load_data
from src.utils.slack_alert import slack_failed_task_alert
from src.utils.config import load_config

logger = logging.getLogger(__name__)
logger.info("🧹 Initializing rest_to_postgres DAG...")

DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "on_failure_callback": slack_failed_task_alert,
    "retries": 1,
}

CONFIG_PATH = os.getenv("REST_TO_POSTGRES_CONFIG_PATH", "/opt/airflow/config/rest_config.yaml")

def create_rest_to_postgres_dag(config_path=CONFIG_PATH):
    with DAG(
        dag_id="rest_to_postgres",
        start_date=datetime(2024, 1, 1),
        schedule_interval="@daily",
        catchup=False,
        default_args=DEFAULT_ARGS,
        tags=["etl", "alpha_vantage"],
    ) as dag:

        def extract_task(ti, **kwargs):
            config = load_config(config_path)
            logger.info("📦 Starting extraction task.")
            data = extract_data(config)
            if not data:
                raise ValueError("❌ Extraction failed.")
            ti.xcom_push(key='raw_data', value=data)

        def transform_task(ti, **kwargs):
            config = load_config(config_path)
            raw_data = ti.xcom_pull(key='raw_data', task_ids='extract')
            processed, failed = process_raw_data(raw_data, config)
            if not processed:
                raise ValueError("❌ Transformation yielded no valid data.")
            ti.xcom_push(key='processed_data', value=processed)

        def load_task(ti, **kwargs):
            config = load_config(config_path)
            processed = ti.xcom_pull(key='processed_data', task_ids='transform')
            inserted_count = load_data(processed, config)
            logger.info(f"✅ {inserted_count} records inserted into PostgreSQL.")

        extract = PythonOperator(task_id="extract", python_callable=extract_task)
        transform = PythonOperator(task_id="transform", python_callable=transform_task)
        load = PythonOperator(task_id="load", python_callable=load_task)

        extract >> transform >> load

        return dag

dag = create_rest_to_postgres_dag()