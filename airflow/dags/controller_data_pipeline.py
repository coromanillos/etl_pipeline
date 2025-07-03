###################################################
# Title: controller_data_pipeline.py
# Author: Christopher Romanillos
# Description: Orchestrates full data flow:
# - Archive Postgres to S3
# - Load Postgres to Redshift
# - Cleanup PostgreSQL only if both succeed
# Date: 2025-06-28
###################################################

from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime
import logging

from src.utils.slack_alert import slack_failed_task_alert

# Configure logging
logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "on_failure_callback": slack_failed_task_alert,
}

with DAG(
    dag_id="controller_data_pipeline",
    description="Master DAG that coordinates archival, redshift loading, and cleanup.",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["controller", "orchestration"],
    doc_md="""
    ### Controller DAG
    Coordinates three dependent DAGs:
    - ✅ `archive_postgres_to_s3`: Cold storage archival
    - ✅ `postgres_to_redshift`: BI-ready warehousing
    - ✅ `cleanup_postgres_after_archive`: Only runs if both above succeed
    """,
) as dag:

    logger.info("Initializing controller_data_pipeline DAG...")

    start = EmptyOperator(task_id="start_pipeline")

    trigger_archive = TriggerDagRunOperator(
        task_id="trigger_archive_postgres_to_s3",
        trigger_dag_id="archive_postgres_to_s3",
        wait_for_completion=True,
        reset_dag_run=True,
        trigger_rule="all_success",
    )

    trigger_redshift = TriggerDagRunOperator(
        task_id="trigger_postgres_to_redshift",
        trigger_dag_id="postgres_to_redshift",
        wait_for_completion=True,
        reset_dag_run=True,
        trigger_rule="all_success",
    )

    join = EmptyOperator(
        task_id="wait_for_both_etl_dags",
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    trigger_cleanup = TriggerDagRunOperator(
        task_id="trigger_postgres_cleanup",
        trigger_dag_id="postgres_cleanup",
        wait_for_completion=False,
        reset_dag_run=True,
        trigger_rule="all_success",
    )

    end = EmptyOperator(task_id="pipeline_complete")

    start >> [trigger_archive, trigger_redshift] >> join >> trigger_cleanup >> end
