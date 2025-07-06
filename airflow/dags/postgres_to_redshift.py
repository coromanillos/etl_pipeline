###################################################
# Title: postgres_to_redshift.py
# Description: Moves cleaned data to Redshift
# Date: 2025-07-06 | Version: 2.1 (testable, refactored)
###################################################

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import logging

from src.utils.postgres_extractor import extract_table_data
from src.etl_postgres_to_redshift.data_validator import validate_dataframe
from src.etl_postgres_to_redshift.data_transformer import transform_for_redshift
from src.etl_postgres_to_redshift.redshift_loader import load_data_to_redshift
from src.utils.slack_alert import slack_failed_task_alert
from src.utils.config import load_config

logger = logging.getLogger(__name__)
logger.info("🧹 Initializing postgres_to_redshift DAG...")

DEFAULT_ARGS = {
    "owner": "airflow",
    "retries": 1,
    "on_failure_callback": slack_failed_task_alert,
}

CONFIG_PATH = os.getenv("POSTGRES_TO_REDSHIFT_CONFIG_PATH", "/opt/airflow/config/redshift_config.yaml")

def create_postgres_to_redshift_dag(config_path=CONFIG_PATH):
    with DAG(
        dag_id="postgres_to_redshift",
        start_date=datetime(2024, 1, 1),
        schedule_interval="@daily",
        catchup=False,
        default_args=DEFAULT_ARGS,
        tags=["etl", "postgres", "redshift"],
    ) as dag:

        def validate_transform_load(**kwargs):
            config = load_config(config_path)
            logger.info("Starting Postgres → Redshift pipeline...")

            table_name = config["postgres_loader"]["table"]
            df = extract_table_data(table_name, config)

            if df.empty:
                logger.warning(f"Table '{table_name}' is empty. Skipping load.")
                return

            validate_dataframe(df, table_name, config)
            transformed_df = transform_for_redshift(df, config)
            load_data_to_redshift(transformed_df, table_name, config)

            logger.info("Postgres → Redshift ETL completed successfully.")

        run_etl = PythonOperator(
            task_id="validate_transform_load",
            python_callable=validate_transform_load,
        )

        return dag

dag = create_postgres_to_redshift_dag()
