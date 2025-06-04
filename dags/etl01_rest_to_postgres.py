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

# === Initialize config and logger ===
CONFIG, LOGGER = initialize_pipeline(component_name="etl_dag", config_path="/opt/airflow/config/config.yaml")

# Ensure DB schema exists
Base.metadata.create_all(engine)

# === Define callable wrappers for Airflow tasks ===

def extract_task(**context):
    raw_file_path = extract_data(CONFIG, LOGGER)
    if not raw_file_path:
        raise ValueError("Extraction failed.")
    context['ti'].xcom_push(key='raw_path', value=raw_file_path)

def transform_task(**context):
    raw_path = context['ti'].xcom_pull(key='raw_path', task_ids='extract')
    
    # Use config-defined processed data directory
    processed_data_dir = CONFIG["directories"]["processed_data"]
    os.makedirs(processed_data_dir, exist_ok=True)  # ensure path exists inside container

    processed_file_path = process_raw_data(raw_path, CONFIG, LOGGER)
    if not processed_file_path:
        raise ValueError("Transformation failed.")
    context['ti'].xcom_push(key='processed_path', value=processed_file_path)

def load_task(**context):
    processed_path = context['ti'].xcom_pull(key='processed_path', task_ids='transform')
    load_data(processed_path, CONFIG, LOGGER)

# === Define the DAG ===

with DAG(
    dag_id="etl01_rest_to_postgres",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["etl", "alpha_vantage"],
) as dag:

    t1 = PythonOperator(
        task_id="extract",
        python_callable=extract_task,
        provide_context=True,
    )

    t2 = PythonOperator(
        task_id="transform",
        python_callable=transform_task,
        provide_context=True,
    )

    t3 = PythonOperator(
        task_id="load",
        python_callable=load_task,
        provide_context=True,
    )

    t1 >> t2 >> t3
