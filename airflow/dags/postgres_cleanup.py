###################################################
# Title: postgres_cleanup.py
# Description: Cleans up PostgreSQL after pipeline
# Date: 2025-07-06 | Version: 3.0 (testable, DI-ready)
###################################################

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime
import os
import logging

from src.utils.slack_alert import slack_failed_task_alert
from src.dags.postgres_cleanup.table_cleaner import drop_all_tables
from src.dags.postgres_cleanup.vacuum_executor import vacuum_postgres
from src.dags.postgres_cleanup.cleanup_logger import log_cleanup_summary
from src.utils.cleanup_config_loader import load_cleanup_config

# Dependency-injectable logger
logger = logging.getLogger(__name__)
logger.info("🚀 Initializing postgres_cleanup DAG")

DEFAULT_ARGS = {
    "owner": "airflow",
    "retries": 1,
    "on_failure_callback": slack_failed_task_alert,
}

# Environment-aware config loader
CONFIG_PATH = os.getenv(
    "POSTGRES_CLEANUP_CONFIG_PATH",
    "/opt/airflow/config/cleanup_config.yaml"
)

def create_postgres_cleanup_dag(config_path=CONFIG_PATH):
    with DAG(
        dag_id="postgres_cleanup",
        start_date=datetime(2024, 1, 1),
        schedule_interval=None,
        catchup=False,
        default_args=DEFAULT_ARGS,
        tags=["postgres", "cleanup", "archive"],
    ) as dag:

        config = load_cleanup_config(config_path)

        with TaskGroup("cleanup_postgres") as cleanup_group:

            def task_drop_tables(**kwargs):
                drop_all_tables(config=config, logger=logger)

            def task_vacuum_db(**kwargs):
                vacuum_postgres(config=config, logger=logger)

            def task_log_cleanup(**kwargs):
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

        return dag

dag = create_postgres_cleanup_dag()
