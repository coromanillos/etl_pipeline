from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os

from src.extract import extract_data
from src.transform import process_raw_data
from src.postgres_loader import load_data
from src.utils.pipeline import initialize_pipeline
from src.utils.schema import Base
from src.utils.db_connection import engine

# === Centralized config & logger initialization ===
CONFIG, LOGGER = initialize_pipeline(component_name="etl_dag", config_path="/opt/airflow/config/config.yaml")

# === Ensure schema exists ===
Base.metadata.create_all(engine)

# === Config-driven directories ===
RAW_DATA_DIR = CONFIG["directories"]["raw_data"]
PROCESSED_DATA_DIR = CONFIG["directories"]["processed_data"]

# === Email alert setup (based on config.yaml notifications block) ===
NOTIFICATIONS = CONFIG.get("notifications", {})
ALERT_EMAILS = NOTIFICATIONS.get("recipients", [])
EMAIL_ON_FAILURE = NOTIFICATIONS.get("email_on_failure", True)
EMAIL_ON_RETRY = NOTIFICATIONS.get("email_on_retry", False)

# === Task Callables ===

def extract_task(ti, **kwargs):
    LOGGER.info("Starting extraction task.")
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    raw_file_path = extract_data(CONFIG, LOGGER)
    if not raw_file_path:
        raise ValueError("Extraction failed.")
    ti.xcom_push(key='raw_path', value=raw_file_path)

def transform_task(ti, **kwargs):
    LOGGER.info("Starting transformation task.")
    raw_path = ti.xcom_pull(key='raw_path', task_ids='extract')
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    processed_file_path = process_raw_data(raw_path, CONFIG, LOGGER)
    if not processed_file_path:
        raise ValueError("Transformation failed.")
    ti.xcom_push(key='processed_path', value=processed_file_path)

def load_task(ti, **kwargs):
    LOGGER.info("Starting load task.")
    processed_path = ti.xcom_pull(key='processed_path', task_ids='transform')
    load_data(processed_path, CONFIG, LOGGER)

# === DAG Definition ===

DEFAULT_ARGS = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ALERT_EMAILS,
    'email_on_failure': EMAIL_ON_FAILURE,
    'email_on_retry': EMAIL_ON_RETRY,
    'retries': 1,
}

with DAG(
    dag_id="etl01_rest_to_postgres",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["etl", "alpha_vantage"],
    doc_md="""
    ### ETL Pipeline DAG
    - **Source:** REST API (e.g., Alpha Vantage)
    - **Target:** PostgreSQL
    - **Monitoring:** Fluent Bit → S3, Airflow Email Alerts
    """,
) as dag:

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
