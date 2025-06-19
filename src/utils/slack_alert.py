import os
import requests

def slack_failed_task_alert(context):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        raise ValueError("SLACK_WEBHOOK_URL is not set in environment variables.")

    task_instance = context.get('task_instance')
    dag_id = context.get('dag').dag_id
    task_id = context.get('task_instance').task_id
    execution_date = context.get('execution_date')
    log_url = task_instance.log_url

    message = f"""
    🚨 *Airflow Task Failed*
    • *DAG:* `{dag_id}`
    • *Task:* `{task_id}`
    • *Execution Date:* `{execution_date}`
    • <{log_url}|View Log>
    """

    payload = {"text": message.strip()}
    requests.post(webhook_url, json=payload)
