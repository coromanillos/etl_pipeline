# tests/unit/test_data_validator.py
import pytest
import pandas as pd
from src.etl_postgres_to_redshift.data_validator import validate_dataframe


@pytest.fixture
def config():
    return {}


@patch("src.etl_postgres_to_redshift.data_validator.get_required_columns")
def test_validate_dataframe_valid(mock_required, config):
    mock_required.return_value = ["id", "value"]
    df = pd.DataFrame({"id": [1], "value": ["abc"]})
    assert validate_dataframe(df, "test_table", config) is True


@patch("src.etl_postgres_to_redshift.data_validator.get_required_columns")
def test_validate_dataframe_missing_columns(mock_required, config):
    mock_required.return_value = ["id", "value"]
    df = pd.DataFrame({"id": [1]})
    with pytest.raises(ValueError):
        validate_dataframe(df, "test_table", config)


@patch("src.etl_postgres_to_redshift.data_validator.get_required_columns")
def test_validate_dataframe_nulls(mock_required, config):
    mock_required.return_value = ["id", "value"]
    df = pd.DataFrame({"id": [1], "value": [None]})
    with pytest.raises(ValueError):
        validate_dataframe(df, "test_table", config)


@patch("src.etl_postgres_to_redshift.data_validator.get_required_columns")
def test_validate_dataframe_timestamp_checks(mock_required, config):
    mock_required.return_value = ["id"]
    df = pd.DataFrame({
        "id": [1, 2],
        "timestamp": ["bad", "2024-01-01"]
    })
    with pytest.raises(TypeError):
        validate_dataframe(df, "test_table", config)
