###################################################
# Title: slack_alert.py
# Author: Christopher Romanillos
# Description: Slack alerts on failure, DAG level.
# Date: 06/26/25
###################################################

import os
import requests
import logging
from src.utils.config import get_env_var  

logger = logging.getLogger(__name__)

def slack_failed_task_alert(context, request_fn=requests.post):
    webhook_url = get_env_var("SLACK_WEBHOOK_URL")

    task_instance = context.get("task_instance")
    dag_id = context.get("dag").dag_id
    task_id = task_instance.task_id
    execution_date = context.get("execution_date")
    log_url = task_instance.log_url

    message = (
        f"\U0001F6A8 *Airflow Task Failed*\n"
        f"• *DAG:* `{dag_id}`\n"
        f"• *Task:* `{task_id}`\n"
        f"• *Execution Date:* `{execution_date}`\n"
        f"• <{log_url}|View Log>"
    )

    try:
        response = request_fn(webhook_url, json={"text": message})
        response.raise_for_status()
        logger.info("✅ Slack alert sent", extra={"status": response.status_code})
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Slack alert failed: {e}", exc_info=True)
