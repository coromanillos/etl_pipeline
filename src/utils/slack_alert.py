###################################################
# Title: slack_alert.py
# Author: Christopher Romanillos
# Description: Slack alerts on failure, DAG level.
# Date: 06/26/25
###################################################

import os
import requests
import logging

logger = logging.getLogger(__name__)

def slack_failed_task_alert(context):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        logger.error("SLACK_WEBHOOK_URL not set in environment")
        raise ValueError("SLACK_WEBHOOK_URL not set in environment")

    task_instance = context.get('task_instance')
    dag_id = context.get('dag').dag_id
    task_id = task_instance.task_id
    execution_date = context.get('execution_date')
    log_url = task_instance.log_url

    message = (
        f"\U0001F6A8 *Airflow Task Failed*\n"
        f"\u2022 *DAG:* `{dag_id}`\n"
        f"\u2022 *Task:* `{task_id}`\n"
        f"\u2022 *Execution Date:* `{execution_date}`\n"
        f"\u2022 <{log_url}|View Log>"
    )

    response = requests.post(webhook_url, json={"text": message})
    logger.info("Slack alert sent", extra={"status": response.status_code})
