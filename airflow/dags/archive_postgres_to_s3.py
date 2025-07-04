###################################################
# Title: archive_postgres_to_s3.py
# Author: Christopher Romanillos
# Description: Moves refined data in postgres to s3
# Secondary phase of ETL
# Date: 06/26/25
###################################################

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import logging
import yaml

from src.etl_postgres_to_s3.parquet_converter import convert_to_parquet
from src.etl_postgres_to_s3.s3_uploader import upload_file_to_s3, generate_s3_key
from src.utils.postgres_extractor import get_all_table_names, extract_table_data
from src.utils.slack_alert import slack_failed_task_alert

logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    "owner": "airflow",
    "retries": 1,
    "on_failure_callback": slack_failed_task_alert,
}

def load_config():
    with open("/opt/airflow/config/config.yaml") as f:
        return yaml.safe_load(f)

with DAG(
    dag_id="archive_postgres_to_s3",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["etl", "postgres", "s3"],
    doc_md="""
    ### Postgres to S3 ETL
    - **Source:** PostgreSQL
    - **Intermediate Format:** Parquet
    - **Destination:** AWS S3 (archive bucket)
    """,
) as dag:

    def extract_convert_upload(**kwargs):
        config = load_config()
        logger.info("Starting Postgres → S3 export pipeline...")

        table_names = get_all_table_names(config)
        if not table_names:
            logger.warning("No tables found in schema.")
            return

        run_timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        archive_bucket = config["s3"]["archive_bucket"]

        for table in table_names:
            logger.info(f"Processing table: {table}")
            df = extract_table_data(table, config)
            if df.empty:
                logger.info(f"Table {table} is empty, skipping.")
                continue

            parquet_path = convert_to_parquet(df, table, config, timestamp=run_timestamp)
            logger.info(f"Parquet file created: {parquet_path}")

            s3_key = generate_s3_key(table, config, timestamp=run_timestamp)
            upload_file_to_s3(parquet_path, config, s3_key, bucket_name=archive_bucket)

        logger.info("Postgres → S3 ETL completed successfully.")

    run_etl = PythonOperator(
        task_id="extract_convert_upload",
        python_callable=extract_convert_upload,
    )
