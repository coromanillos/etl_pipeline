# tests/unit/test_aws_client.py

from unittest.mock import MagicMock
from src.utils.aws_client import get_s3_client

def test_get_s3_client_with_localstack():
    config = {
        "use_localstack": True,
        "s3": {
            "region": "us-east-1",
            "endpoint_url": "http://localhost:4566"
        }
    }

    mock_factory = MagicMock()
    get_s3_client(config, client_factory=mock_factory)

    mock_factory.assert_called_with(
        "s3",
        region_name="us-east-1",
        endpoint_url="http://localhost:4566",
        aws_access_key_id="test",
        aws_secret_access_key="test"
    )

def test_get_s3_client_without_localstack():
    config = {
        "s3": {
            "region": "us-west-2"
        }
    }

    mock_factory = MagicMock()
    get_s3_client(config, client_factory=mock_factory)

    mock_factory.assert_called_with("s3", region_name="us-west-2")
