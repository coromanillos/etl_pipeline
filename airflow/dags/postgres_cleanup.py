###################################################
# Title: postgres_cleanup.py
# Description: Cleans up PostgreSQL after pipeline
# Date: 2025-07-21 | Version: 4.1 (Final, autocommit refactor)
###################################################

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from src.utils.slack_alert import slack_failed_task_alert
from src.utils.postgres_cleaner import drop_all_tables, vacuum_postgres
from src.etl_cleanup_postgres_after_archive.cleanup_logger import log_cleanup_summary
from src.etl_cleanup_postgres_after_archive.cleanup_config_loader import load_cleanup_config


DEFAULT_ARGS = {
    "owner": "airflow",
    "retries": 1,
    "on_failure_callback": slack_failed_task_alert,
}

CONFIG = load_cleanup_config()


def drop_tables_task(**context):
    """Drops all tables in the target PostgreSQL schema."""
    drop_all_tables(config=CONFIG)


def vacuum_db_task(**context):
    """Performs VACUUM FULL on PostgreSQL. Now correctly uses autocommit via refactored utility."""
    vacuum_postgres(config=CONFIG)


def log_cleanup_task(**context):
    """Logs a message indicating cleanup completion."""
    log_cleanup_summary(
        config=CONFIG,
        message="✅ PostgreSQL cleanup completed successfully."
    )


with DAG(
    dag_id="postgres_cleanup",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["postgres", "cleanup", "archive"],
) as dag:

    drop_tables = PythonOperator(
        task_id="drop_all_postgres_tables",
        python_callable=drop_tables_task,
    )

    vacuum_db = PythonOperator(
        task_id="run_vacuum_full",
        python_callable=vacuum_db_task,
    )

    log_cleanup = PythonOperator(
        task_id="log_cleanup_operation",
        python_callable=log_cleanup_task,
    )

    drop_tables >> vacuum_db >> log_cleanup
