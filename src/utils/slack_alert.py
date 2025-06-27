###################################################
# Title: slack_alert.py
# Author: Christopher Romanillos
# Description: Slack alerts on failure, DAG level.
# Date: 06/26/25
###################################################

import os
import requests

def slack_failed_task_alert(context):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        raise ValueError("SLACK_WEBHOOK_URL not set in environment")

    task_instance = context.get('task_instance')
    dag_id = context.get('dag').dag_id
    task_id = task_instance.task_id
    execution_date = context.get('execution_date')
    log_url = task_instance.log_url

    message = (
        f"🚨 *Airflow Task Failed*\n"
        f"• *DAG:* `{dag_id}`\n"
        f"• *Task:* `{task_id}`\n"
        f"• *Execution Date:* `{execution_date}`\n"
        f"• <{log_url}|View Log>"
    )

    requests.post(webhook_url, json={"text": message})
