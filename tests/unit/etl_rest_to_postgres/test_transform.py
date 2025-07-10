# File: tests/unit/test_rest_to_postgres/test_transformer.py
import pytest
from src.etl_rest_to_postgres.transform import process_raw_data

@pytest.fixture
def config():
    return {"transform": {"required_fields": ["1. open", "2. high", "3. low", "4. close", "5. volume"]}}

@pytest.fixture
def valid_raw_data():
    return {
        "Time Series (5min)": {
            "2024-10-10 10:00:00": {
                "1. open": "100.0",
                "2. high": "105.0",
                "3. low": "99.5",
                "4. close": "102.0",
                "5. volume": "1000"
            }
        }
    }

def test_process_raw_data_success(valid_raw_data, config):
    processed, failed = process_raw_data(valid_raw_data, config)
    assert isinstance(processed, list)
    assert len(processed) == 1
    assert failed == []

def test_process_raw_data_missing_series(config):
    processed, failed = process_raw_data({}, config)
    assert processed is None
    assert failed is None

def test_process_raw_data_missing_fields(config):
    raw_data = {"Time Series (5min)": {"2024-10-10 10:00:00": {"1. open": "100.0"}}}
    processed, failed = process_raw_data(raw_data, config)
    assert processed is None  # changed
    assert len(failed) == 1
