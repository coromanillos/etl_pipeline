###################################################
# Title: slack_alert.py
# Author: Christopher Romanillos
# Description: Slack alerts on failure, DAG level.
# Date: 06/26/25
###################################################

import logging
import requests
from typing import Any, Callable
from src.utils.config import get_env_var

logger = logging.getLogger(__name__)


def slack_failed_task_alert(context: dict, request_fn: Callable = requests.post) -> None:
    """
    Sends a Slack alert when a DAG task fails.

    Args:
        context (dict): Airflow task context dictionary.
        request_fn (Callable): HTTP request function, defaults to requests.post.
    """
    webhook_url = get_env_var("SLACK_WEBHOOK_URL")
    if not webhook_url:
        logger.warning("⚠️ SLACK_WEBHOOK_URL is not set. Slack alert will not be sent.")
        return

    try:
        task_instance = context.get("task_instance")
        dag_id = context.get("dag").dag_id
        task_id = task_instance.task_id
        execution_date = context.get("execution_date")
        log_url = task_instance.log_url

        message = (
            f"🚨 *Airflow Task Failed*\n"
            f"• *DAG:* `{dag_id}`\n"
            f"• *Task:* `{task_id}`\n"
            f"• *Execution Date:* `{execution_date}`\n"
            f"• <{log_url}|View Log>"
        )

        response = request_fn(webhook_url, json={"text": message})
        response.raise_for_status()
        logger.info("✅ Slack alert sent successfully", extra={"status": response.status_code})

    except Exception as e:
        logger.error("❌ Slack alert failed", exc_info=True)
