from sqlalchemy import DateTime, Float, BigInteger
from src.utils.schema import get_table_column_types, get_required_columns

def test_get_table_column_types():
    """Verify returned dictionary maps columns to expected SQLAlchemy types."""
    types = get_table_column_types()
    assert types["timestamp"] == DateTime
    assert types["open"] == Float
    assert types["volume"] == BigInteger
    assert set(types.keys()) == {"timestamp", "open", "high", "low", "close", "volume"}

def test_get_required_columns():
    """Verify required columns list."""
    required = get_required_columns()
    assert isinstance(required, list)
    assert set(required) == {"timestamp", "open", "high", "low", "close", "volume"}
