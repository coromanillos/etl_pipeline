# tests/unit/conftest.py

import pytest
from unittest.mock import MagicMock, patch

pytestmark = pytest.mark.unit

@pytest.fixture
def mock_db_conn():
    with patch("src.utils.db_client.get_postgres_connection") as mock:
        yield mock

@pytest.fixture
def mock_s3_client():
    with patch("src.utils.aws_client.get_s3_client") as mock:
        yield mock
