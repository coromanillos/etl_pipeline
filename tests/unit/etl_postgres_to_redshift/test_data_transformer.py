import pytest
import pandas as pd
from unittest.mock import patch

from src.etl_postgres_to_redshift.data_transformer import transform_for_redshift

# Mock SQLAlchemy-like type classes
class MockDateTime:
    __name__ = "DateTime"

class MockFloat:
    __name__ = "Float"

class MockBigInteger:
    __name__ = "BigInteger"

@pytest.fixture
def mock_column_types():
    return {
        "timestamp": MockDateTime(),
        "price": MockFloat(),
        "volume": MockBigInteger(),
    }

@pytest.fixture
def config_stub():
    return {"redshift": {"schema": "public", "table": "market_data"}}

@pytest.fixture(autouse=True)
def patch_get_table_column_types(mock_column_types):
    with patch("src.etl_postgres_to_redshift.data_transformer.get_table_column_types", return_value=mock_column_types):
        yield

def test_transform_with_valid_data(config_stub):
    df = pd.DataFrame({
        "timestamp": ["2024-06-01 14:00:00", "2024-06-01 14:05:00"],
        "price": ["150.0", "152.5"],
        "volume": ["1000", "2000"]
    })

    result = transform_for_redshift(df.copy(), config_stub)

    assert pd.api.types.is_datetime64_any_dtype(result["timestamp"]), "Timestamp not converted to datetime"
    assert pd.api.types.is_float_dtype(result["price"]), "Price not converted to float"
    assert pd.api.types.is_integer_dtype(result["volume"]), "Volume not converted to integer"
    assert not result.isnull().values.any(), "DataFrame contains unexpected nulls"

def test_transform_with_missing_column(config_stub):
    df = pd.DataFrame({
        "timestamp": ["2024-06-01 14:00:00"],
        "price": ["151.0"]
        # volume is missing
    })

    result = transform_for_redshift(df.copy(), config_stub)

    assert "volume" not in result.columns or result["volume"].isnull().all(), "Missing column should be null or excluded"

def test_transform_empty_dataframe(config_stub):
    df = pd.DataFrame()

    result = transform_for_redshift(df, config_stub)

    assert result.empty, "Expected empty DataFrame"

def test_transform_with_invalid_data(config_stub):
    df = pd.DataFrame({
        "timestamp": ["not a date", "still not a date"],
        "price": ["bad", "data"],
        "volume": ["NaN", "also bad"]
    })

    result = transform_for_redshift(df.copy(), config_stub)

    assert result["timestamp"].isnull().all(), "Invalid timestamps not coerced to NaT"
    assert result["price"].isnull().all(), "Invalid prices not coerced to NaN"
    assert result["volume"].isnull().all(), "Invalid volume not coerced to NaN"
