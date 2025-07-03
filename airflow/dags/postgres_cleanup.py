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

from src.dags.postgres_cleanup.cleanup_config_loader import load_cleanup_config
from src.dags.postgres_cleanup.table_cleaner import drop_all_tables
from src.dags.postgres_cleanup.vacuum_executor import vacuum_postgres
from src.dags.postgres_cleanup.cleanup_logger import log_cleanup_summary
from src.utils.slack_alert import slack_failed_task_alert

# Load pipeline config and logger
CONFIG, logger = load_cleanup_config()

DEFAULT_ARGS = {
    "owner": "airflow",
    "retries": 1,
    "on_failure_callback": slack_failed_task_alert,
}

with DAG(
    dag_id="postgres_cleanup",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,  # Triggered manually or by controller DAG
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["postgres", "cleanup", "archive"],
    doc_md="""
    ### PostgreSQL Cleanup DAG
    - Drops all tables from PostgreSQL
    - Runs `VACUUM FULL` to reclaim space
    - Logs cleanup completion
    - Assumes `archive_postgres_to_s3` DAG has completed successfully
    """,
) as dag:

    logger.info("🧹 postgres_cleanup DAG initialized...")

    with TaskGroup("cleanup_postgres") as cleanup_group:

        drop_tables = PythonOperator(
            task_id="drop_all_postgres_tables",
            python_callable=drop_all_tables,
            op_kwargs={"config": CONFIG, "logger": logger},
        )

        vacuum_db = PythonOperator(
            task_id="run_vacuum_full",
            python_callable=vacuum_postgres,
            op_kwargs={"config": CONFIG, "logger": logger},
        )

        log_cleanup = PythonOperator(
            task_id="log_cleanup_operation",
            python_callable=log_cleanup_summary,
            op_kwargs={
                "config": CONFIG,
                "logger": logger,
                "message": "✅ PostgreSQL cleanup completed successfully.",
            },
        )

        drop_tables >> vacuum_db >> log_cleanup

    cleanup_group
