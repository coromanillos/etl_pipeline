import pytest
import pandas as pd
from unittest.mock import patch

from src.etl_postgres_to_redshift.data_transformer import transform_for_redshift

@pytest.fixture
def mock_column_types():
    return {
        "timestamp": type("DateTime", (), {})(),
        "price": type("Float", (), {})(),
        "volume": type("BigInteger", (), {})(),
    }

@pytest.fixture
def config_stub():
    return {"redshift": {"schema": "public", "table": "market_data"}}

def test_transform_with_valid_data(mock_column_types, config_stub):
    df = pd.DataFrame({
        "timestamp": ["2024-06-01 14:00:00", "2024-06-01 14:05:00"],
        "price": ["150.0", "152.5"],
        "volume": ["1000", "2000"]
    })

    with patch("src.etl_postgres_to_redshift.data_transformer.get_table_column_types", return_value=mock_column_types):
        result = transform_for_redshift(df.copy(), config_stub)

    assert pd.api.types.is_datetime64_any_dtype(result["timestamp"])
    assert pd.api.types.is_float_dtype(result["price"])
    assert pd.api.types.is_integer_dtype(result["volume"])
    assert not result.isnull().values.any()

def test_transform_with_missing_column(mock_column_types, config_stub):
    df = pd.DataFrame({
        "timestamp": ["2024-06-01 14:00:00"],
        "price": ["151.0"]
        # 'volume' is missing
    })

    with patch("src.etl_postgres_to_redshift.data_transformer.get_table_column_types", return_value=mock_column_types):
        result = transform_for_redshift(df.copy(), config_stub)

    assert "volume" not in result.columns or result["volume"].isnull().all()

def test_transform_empty_dataframe(mock_column_types, config_stub):
    df = pd.DataFrame()

    with patch("src.etl_postgres_to_redshift.data_transformer.get_table_column_types", return_value=mock_column_types):
        result = transform_for_redshift(df, config_stub)

    assert result.empty

def test_transform_with_invalid_data(mock_column_types, config_stub):
    df = pd.DataFrame({
        "timestamp": ["not a date", "still not a date"],
        "price": ["bad", "data"],
        "volume": ["NaN", "also bad"]
    })

    with patch("src.etl_postgres_to_redshift.data_transformer.get_table_column_types", return_value=mock_column_types):
        result = transform_for_redshift(df.copy(), config_stub)

    # All coerced to NaT or NaN
    assert result["timestamp"].isnull().all()
    assert result["price"].isnull().all()
    assert result["volume"].isnull().all()
