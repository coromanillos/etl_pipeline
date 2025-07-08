import pytest
from unittest.mock import MagicMock
from src.utils.api_requests import fetch_data
import requests

@pytest.fixture
def sample_config():
    return {
        "endpoint": "https://api.example.com",
        "timeout": 10,
        "symbol": "IBM",
        "interval": "5min",
        "key": "demo-key"
    }

def test_fetch_data_success(sample_config):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "some_result"}
    mock_response.raise_for_status.return_value = None

    mock_get = MagicMock(return_value=mock_response)

    result = fetch_data(sample_config, request_fn=mock_get)

    assert result == {"data": "some_result"}
    mock_get.assert_called_once()

@pytest.mark.parametrize("exception_type", [
    requests.exceptions.Timeout,
    requests.exceptions.ConnectionError,
    requests.exceptions.HTTPError,
    requests.exceptions.RequestException
])
def test_fetch_data_errors(sample_config, exception_type):
    mock_get = MagicMock(side_effect=exception_type("Simulated error"))

    with pytest.raises(exception_type):
        fetch_data(sample_config, request_fn=mock_get)
