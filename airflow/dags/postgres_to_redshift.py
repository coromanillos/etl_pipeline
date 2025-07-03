###################################################
# Title: etl03_postgres_to_redshift.py
# Author: Christopher Romanillos
# Description: Moves cleaned data from PostgreSQL
# to Amazon Redshift with schema-based validation
# and transformation.
# Date: 06/28/25
###################################################

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import logging
import pandas as pd

from src.utils.pipeline import initialize_pipeline
from src.utils.slack_alert import slack_failed_task_alert

from src.etl_postgres_to_redshift.postgres_extractor import extract_table_data
from src.etl_postgres_to_redshift.data_validator import validate_dataframe
from src.etl_postgres_to_redshift.data_transformer import transform_for_redshift
from src.etl_postgres_to_redshift.redshift_loader import load_data_to_redshift

# Initialize config once (inherits ENV and YAML)
CONFIG, _ = initialize_pipeline(component_name="postgres_to_redshift", config_path="/opt/airflow/config/config.yaml")

logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    "owner": "airflow",
    "retries": 1,
    "on_failure_callback": slack_failed_task_alert,
}

with DAG(
    dag_id="etl03_postgres_to_redshift",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["etl", "postgres", "redshift"],
    doc_md="""
    ### Postgres to Redshift ETL
    - **Source:** PostgreSQL
    - **Destination:** Amazon Redshift
    - **Steps:** Validate → Transform → Load
    """,
) as dag:

    def validate_transform_load(**kwargs):
        logger.info("Starting Postgres → Redshift pipeline...")

        table_name = CONFIG["postgres_loader"]["table"]
        df = extract_table_data(table_name, CONFIG)

        if df.empty:
            logger.warning(f"Table '{table_name}' is empty. Skipping load.")
            return

        # Validate against schema-based rules
        validate_dataframe(df, table_name)

        # Transform for Redshift compatibility
        transformed_df = transform_for_redshift(df)

        # Load to Redshift
        load_data_to_redshift(transformed_df, table_name, CONFIG)

        logger.info("Postgres → Redshift ETL completed successfully.")

    run_etl = PythonOperator(
        task_id="validate_transform_load",
        python_callable=validate_transform_load,
    )
