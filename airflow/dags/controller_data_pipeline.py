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

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="controller_data_pipeline",
    description="Master DAG that coordinates archival, redshift loading, and cleanup.",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args=default_args,
    tags=["controller", "orchestration"],
    doc_md="""
    ### Controller DAG
    Coordinates three dependent DAGs:
    - ✅ `archive_postgres_to_s3`: Cold storage archival
    - ✅ `postgres_to_redshift`: BI-ready warehousing
    - ✅ `cleanup_postgres_after_archive`: Only runs if both above succeed
    """,
) as dag:

    start = EmptyOperator(task_id="start_pipeline")

    # Trigger archival DAG
    trigger_archive = TriggerDagRunOperator(
        task_id="trigger_archive_postgres_to_s3",
        trigger_dag_id="archive_postgres_to_s3",
        wait_for_completion=True,
        reset_dag_run=True,
        trigger_rule="all_success",
    )

    # Trigger redshift DAG
    trigger_redshift = TriggerDagRunOperator(
        task_id="trigger_postgres_to_redshift",
        trigger_dag_id="postgres_to_redshift",
        wait_for_completion=True,
        reset_dag_run=True,
        trigger_rule="all_success",
    )

    # Wait until both complete before cleanup
    join = EmptyOperator(
        task_id="wait_for_both_etl_dags",
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    # Trigger cleanup DAG
    trigger_cleanup = TriggerDagRunOperator(
        task_id="trigger_postgres_cleanup",
        trigger_dag_id="postgres_cleanup",
        wait_for_completion=False,
        reset_dag_run=True,
        trigger_rule="all_success",
    )

    end = EmptyOperator(task_id="pipeline_complete")

    # Define full flow
    start >> [trigger_archive, trigger_redshift] >> join >> trigger_cleanup >> end
