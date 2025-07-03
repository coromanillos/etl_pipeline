###################################################
# Title: etl01_rest_to_postgres.py
# Author: Christopher Romanillos
# Description: Moves weekly api data to postgres
# First phase of ETL
# Date: 06/26/25
###################################################

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import logging
from dotenv import load_dotenv
import yaml

from src.etl_rest_to_postgres.extract import extract_data
from src.etl_rest_to_postgres.transform import process_raw_data
from src.etl_rest_to_postgres.postgres_loader import load_data
from src.utils.schema import Base
from src.utils.db_connection import engine
from src.utils.slack_alert import slack_failed_task_alert

logger = logging.getLogger(__name__)

# Load env vars and config once
load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "..", "config", "config.yaml")

with open(CONFIG_PATH, "r") as f:
    CONFIG = yaml.safe_load(f)

# Ensure schema exists
Base.metadata.create_all(engine)

# Config-driven directories
RAW_DATA_DIR = CONFIG["directories"]["raw_data"]
PROCESSED_DATA_DIR = CONFIG["directories"]["processed_data"]

DEFAULT_ARGS = {
    'owner': 'airflow',
    'depends_on_past': False,
    'on_failure_callback': slack_failed_task_alert,
    'retries': 1,
}

with DAG(
    dag_id="rest_to_postgres",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["etl", "alpha_vantage"],
    doc_md="""
    ### ETL Pipeline DAG
    - **Source:** REST API (e.g., Alpha Vantage)
    - **Target:** PostgreSQL
    - **Monitoring:** Slack Alerts via on_failure_callback
    """,
) as dag:

    def extract_task(ti, **kwargs):
        logger.info("Starting extraction task.")
        os.makedirs(RAW_DATA_DIR, exist_ok=True)
        raw_file_path = extract_data(CONFIG)
        if not raw_file_path:
            raise ValueError("Extraction failed.")
        ti.xcom_push(key='raw_path', value=raw_file_path)

    def transform_task(ti, **kwargs):
        logger.info("Starting transformation task.")
        raw_path = ti.xcom_pull(key='raw_path', task_ids='extract')
        os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
        processed_file_path = process_raw_data(raw_path, CONFIG)
        if not processed_file_path:
            raise ValueError("Transformation failed.")
        ti.xcom_push(key='processed_path', value=processed_file_path)

    def load_task(ti, **kwargs):
        logger.info("Starting load task.")
        processed_path = ti.xcom_pull(key='processed_path', task_ids='transform')
        load_data(processed_path, CONFIG)

    extract = PythonOperator(
        task_id="extract",
        python_callable=extract_task,
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=transform_task,
    )

    load = PythonOperator(
        task_id="load",
        python_callable=load_task,
    )

    extract >> transform >> load
