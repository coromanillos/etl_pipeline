# tests/unit/test_postgres_loader.py

import pytest
from unittest.mock import MagicMock
from datetime import datetime
from src.etl_rest_to_postgres.postgres_loader import load_data

@pytest.fixture
def sample_data():
    return [
        {
            "timestamp": "2025-07-06T12:00:00",
            "open": "100.5",
            "high": "110.0",
            "low": "95.0",
            "close": "105.5",
            "volume": "10000"
        },
        {
            "timestamp": "invalid-timestamp",
            "open": "abc",
            "high": "110.0",
            "low": "95.0",
            "close": "105.5",
            "volume": "10000"
        },
        {
            # Missing required field "volume"
            "timestamp": "2025-07-06T13:00:00",
            "open": "101",
            "high": "111",
            "low": "96",
            "close": "106"
        }
    ]

@pytest.fixture
def config():
    return {"postgres_loader": {"connection_string": "postgresql://user:pass@localhost/db"}}

def test_load_data_success(sample_data, config):
    mock_session = MagicMock()
    mock_factory = MagicMock(return_value=mock_session)
    mock_session.__enter__.return_value = mock_session

    inserted = load_data(sample_data, config, session_factory=mock_factory)

    # Only 1 record is valid (first one)
    assert inserted == 1
    assert mock_session.bulk_save_objects.call_count == 1
    assert mock_session.commit.call_count == 1

def test_load_data_empty_input(config):
    result = load_data([], config)
    assert result == 0

def test_load_data_no_valid_records(config):
    # All invalid records (missing required fields)
    invalid_data = [{"timestamp": "2025-07-06T12:00:00"}]
    result = load_data(invalid_data, config)
    assert result == 0

def test_load_data_db_failure(sample_data, config):
    mock_session = MagicMock()
    mock_factory = MagicMock(return_value=mock_session)
    mock_session.__enter__.return_value = mock_session
    mock_session.bulk_save_objects.side_effect = Exception("DB error")

    result = load_data(sample_data, config, session_factory=mock_factory)
    assert result == 0
