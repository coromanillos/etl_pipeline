##############################################
# Title: postgres_cleanup.py
# Author: Christopher Romanillos
# Description: Empties PostgreSQL after pipeline completion,
#   ensures that PostgreSQL starts clean whenever executed.
# Date: 06/29/25
##############################################

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime
import logging

from src.utils.slack_alert import slack_failed_task_alert
from src.dags.postgres_cleanup.table_cleaner import drop_all_tables
from src.dags.postgres_cleanup.vacuum_executor import vacuum_postgres
from src.dags.postgres_cleanup.cleanup_logger import log_cleanup_summary
from src.utils.pipeline import initialize_pipeline
from src.utils.config import load_config

DEFAULT_ARGS = {
    "owner": "airflow",
    "retries": 1,
    "on_failure_callback": slack_failed_task_alert,
}

def get_config_and_logger():
    config = load_config("/opt/airflow/config/cleanup_config.yaml")
    logger = initialize_pipeline("postgres_cleanup")
    return config, logger

with DAG(
    dag_id="postgres_cleanup",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["postgres", "cleanup", "archive"],
) as dag:

    with TaskGroup("cleanup_postgres") as cleanup_group:

        def task_drop_tables(**kwargs):
            config, logger = get_config_and_logger()
            drop_all_tables(config=config, logger=logger)

        def task_vacuum_db(**kwargs):
            config, logger = get_config_and_logger()
            vacuum_postgres(config=config, logger=logger)

        def task_log_cleanup(**kwargs):
            config, logger = get_config_and_logger()
            log_cleanup_summary(
                config=config,
                logger=logger,
                message="✅ PostgreSQL cleanup completed successfully."
            )

        drop_tables = PythonOperator(
            task_id="drop_all_postgres_tables",
            python_callable=task_drop_tables,
        )

        vacuum_db = PythonOperator(
            task_id="run_vacuum_full",
            python_callable=task_vacuum_db,
        )

        log_cleanup = PythonOperator(
            task_id="log_cleanup_operation",
            python_callable=task_log_cleanup,
        )

        drop_tables >> vacuum_db >> log_cleanup