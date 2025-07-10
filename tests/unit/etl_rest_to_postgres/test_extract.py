# tests/unit/dags/test_rest_to_postgres/test_extractor.py
import pytest
from unittest.mock import MagicMock
from src.etl_rest_to_postgres.extract import extract_data

def test_extract_data_success():
    mock_fetch = MagicMock(return_value={"Time Series (5min)": {}})
    config = {"api": {}}
    result = extract_data(config, fetch_fn=mock_fetch)
    assert result == {"Time Series (5min)": {}}

def test_extract_data_empty():
    mock_fetch = MagicMock(return_value=None)
    config = {"api": {}}
    result = extract_data(config, fetch_fn=mock_fetch)
    assert result is None

def test_extract_data_exception():
    mock_fetch = MagicMock(side_effect=Exception("API failure"))
    config = {"api": {}}
    result = extract_data(config, fetch_fn=mock_fetch)
    assert result is None
