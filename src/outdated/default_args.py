# Default arguments for Slack *dummy messages*

from datetime import timedelta
from src.utils.slack_alert import slack_failed_task_alert
from src.utils.pipeline import initialize_pipeline

CONFIG, _ = initialize_pipeline("default_args", "/opt/airflow/config/config.yaml")

NOTIFICATIONS = CONFIG.get("notifications", {})
ALERT_EMAILS = NOTIFICATIONS.get("recipients", [])
EMAIL_ON_FAILURE = NOTIFICATIONS.get("email_on_failure", True)
EMAIL_ON_RETRY = NOTIFICATIONS.get("email_on_retry", False)

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email": ALERT_EMAILS,
    "email_on_failure": EMAIL_ON_FAILURE,
    "email_on_retry": EMAIL_ON_RETRY,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "on_failure_callback": slack_failed_task_alert,
}
