###################################################
# Title: controller_data_pipeline.py
# Description: Orchestrates all DAGs
# Date: 2025-07-06 | Version: 2.1 (testable, refactored)
###################################################

from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime
import logging

from src.utils.slack_alert import slack_failed_task_alert
from src.utils.config import get_env_var

logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "on_failure_callback": slack_failed_task_alert,
}

def create_controller_data_pipeline_dag():
    # Check required env vars at runtime, not import time
    slack_webhook = get_env_var("SLACK_WEBHOOK_URL", required=True)
    logger.info("🚀 Initializing controller_data_pipeline DAG")

    with DAG(
        dag_id="controller_data_pipeline",
        description="Master DAG that coordinates archival, redshift loading, and cleanup.",
        start_date=datetime(2024, 1, 1),
        schedule_interval="@daily",
        catchup=False,
        default_args=DEFAULT_ARGS,
        tags=["controller", "orchestration"],
    ) as dag:

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

        return dag

dag = create_controller_data_pipeline_dag()
