import pytest
from datetime import datetime
from src.utils.data_validation import transform_and_validate_data

@pytest.fixture
def required_fields():
    return ["1. open", "2. high", "3. low", "4. close", "5. volume"]

def test_transform_valid_data(required_fields):
    input_item = (
        "2025-06-20 12:30:00",
        {
            "1. open": "100.5",
            "2. high": "105.0",
            "3. low": "99.0",
            "4. close": "102.0",
            "5. volume": "10000"
        }
    )

    result = transform_and_validate_data(input_item, required_fields)

    assert result["timestamp"] == datetime(2025, 6, 20, 12, 30, 0)
    assert result["open"] == 100.5
    assert result["volume"] == 10000

def test_transform_missing_fields(required_fields):
    input_item = (
        "2025-06-20 12:30:00",
        {
            "1. open": "100.5",
            "2. high": "105.0"
        }
    )

    result = transform_and_validate_data(input_item, required_fields)
    assert result is None

def test_transform_invalid_data(required_fields):
    input_item = (
        "2025-06-20 12:30:00",
        {
            "1. open": "abc",  # invalid float
            "2. high": "105.0",
            "3. low": "99.0",
            "4. close": "102.0",
            "5. volume": "10000"
        }
    )

    result = transform_and_validate_data(input_item, required_fields)
    assert result is None
