import pytest
from unittest.mock import MagicMock, patch
from src.utils.slack_alert import slack_failed_task_alert

@patch("src.utils.slack_alert.get_env_var", return_value="https://fake-webhook.url")
@patch("src.utils.slack_alert.logger")
def test_slack_failed_task_alert_success(mock_logger, mock_get_env_var):
    """Test Slack alert sends a successful POST request and logs info."""
    mock_post = MagicMock()
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    context = {
        "task_instance": MagicMock(task_id="task1", log_url="http://log.url"),
        "dag": MagicMock(dag_id="dag1"),
        "execution_date": "2025-07-08T12:00:00",
    }

    slack_failed_task_alert(context, request_fn=mock_post)

    mock_post.assert_called_once()
    mock_response.raise_for_status.assert_called_once()
    mock_logger.info.assert_called_once_with("✅ Slack alert sent", extra={"status": 200})

@patch("src.utils.slack_alert.get_env_var", return_value="https://fake-webhook.url")
@patch("src.utils.slack_alert.logger")
def test_slack_failed_task_alert_failure(mock_logger, mock_get_env_var):
    """Test Slack alert logs error on failed POST request."""
    mock_post = MagicMock()
    mock_post.side_effect = Exception("failed request")

    context = {
        "task_instance": MagicMock(task_id="task1", log_url="http://log.url"),
        "dag": MagicMock(dag_id="dag1"),
        "execution_date": "2025-07-08T12:00:00",
    }

    slack_failed_task_alert(context, request_fn=mock_post)

    mock_logger.error.assert_called()
