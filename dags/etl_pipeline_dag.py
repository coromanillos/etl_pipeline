from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from src.extract import extract_data
from src.transform import process_raw_data
from src.postgres_loader import load_data
from src.utils.pipeline import initialize_pipeline
from src.utils.schema import Base
from src.utils.db_connection import engine

# Global vars to re-use across tasks
CONFIG, LOGGER = initialize_pipeline(component_name="etl_dag", config_path="../config/config.yaml")

# Ensure DB schema exists (this can also be made into its own task if desired)
Base.metadata.create_all(engine)

# === Define callable wrappers for Airflow tasks ===

def extract_task(**context):
    raw_file_path = extract_data(CONFIG, LOGGER)
    if not raw_file_path:
        raise ValueError("Extraction failed.")
    context['ti'].xcom_push(key='raw_path', value=raw_file_path)

def transform_task(**context):
    raw_path = context['ti'].xcom_pull(key='raw_path', task_ids='extract')
    processed_file_path = process_raw_data(raw_path, CONFIG, LOGGER)
    if not processed_file_path:
        raise ValueError("Transformation failed.")
    context['ti'].xcom_push(key='processed_path', value=processed_file_path)

def load_task(**context):
    processed_path = context['ti'].xcom_pull(key='processed_path', task_ids='transform')
    load_data(processed_path, CONFIG, LOGGER)

# === Define the DAG ===

with DAG(
    dag_id="alpha_vantage_etl",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",  # or cron expression like "0 7 * * *"
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
