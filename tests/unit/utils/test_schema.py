# tests/unit/utils/test_schema.py

from sqlalchemy import DateTime, Float, BigInteger
from src.utils.schema import get_table_column_types, get_required_columns


def test_get_table_column_types():
    """Ensure get_table_column_types returns correct SQLAlchemy types."""
    types = get_table_column_types()

    assert types["timestamp"] == DateTime
    assert types["open"] == Float
    assert types["high"] == Float
    assert types["low"] == Float
    assert types["close"] == Float
    assert types["volume"] == BigInteger

    assert set(types.keys()) == {"timestamp", "open", "high", "low", "close", "volume"}
    assert len(types) == 6


def test_get_required_columns():
    """Ensure get_required_columns returns expected column names."""
    required = get_required_columns()

    assert isinstance(required, list)
    assert len(required) == 6
    assert set(required) == {"timestamp", "open", "high", "low", "close", "volume"}
