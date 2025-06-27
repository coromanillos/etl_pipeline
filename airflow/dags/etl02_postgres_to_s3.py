###################################################
# Title: etl02_postgres_to_s3.py
# Author: Christopher Romanillos
# Description: Moves refined data in postgres to s3
# Secondary phase of ETL
# Date: 06/26/25
###################################################

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import logging

from src.etl_postgres_to_s3.postgres_extractor import get_all_table_names, extract_table_data
from src.etl_postgres_to_s3.parquet_converter import convert_to_parquet
from src.etl_postgres_to_s3.s3_uploader import upload_file_to_s3, generate_s3_key
from src.utils.pipeline import initialize_pipeline
from src.utils.slack_alert import slack_failed_task_alert  

# Initialize config once here in DAG
CONFIG, _ = initialize_pipeline(component_name="etl02_postgres_to_s3", config_path="/opt/airflow/config/config.yaml")

logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    "owner": "airflow",
    "retries": 1,
    "on_failure_callback": slack_failed_task_alert,  
}

with DAG(
    dag_id="etl02_postgres_to_s3",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["etl", "postgres", "s3"],
    doc_md="""
    ### Postgres to S3 ETL
    - **Source:** PostgreSQL
    - **Intermediate Format:** Parquet
    - **Destination:** AWS S3
    """,
) as dag:

    def extract_convert_upload(**kwargs):
        logger.info("Starting Postgres → S3 export pipeline...")

        table_names = get_all_table_names(CONFIG)
        if not table_names:
            logger.warning("No tables found in schema.")
            return

        for table in table_names:
            logger.info(f"Processing table: {table}")
            df = extract_table_data(table, CONFIG)
            if df.empty:
                logger.info(f"Table {table} is empty, skipping.")
                continue

            parquet_path = convert_to_parquet(df, table, CONFIG)
            logger.info(f"Parquet file created: {parquet_path}")

            s3_key = generate_s3_key(table, CONFIG)
            upload_file_to_s3(parquet_path, CONFIG, s3_key)


        logger.info("Postgres → S3 ETL completed successfully.")

    run_etl = PythonOperator(
        task_id="extract_convert_upload",
        python_callable=extract_convert_upload,
    )
