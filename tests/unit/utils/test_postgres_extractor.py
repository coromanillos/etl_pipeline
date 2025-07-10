import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from src.utils.postgres_extractor import get_all_table_names, extract_table_data

@pytest.fixture
def mock_config():
    return {"postgres_loader": {"connection_string": "postgresql://...", "schema": "public"}}

def test_get_all_table_names_success(mock_config):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [("table1",), ("table2",)]

    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    mock_factory = MagicMock(return_value=MagicMock(__enter__=lambda x: mock_conn, __exit__=MagicMock()))

    tables = get_all_table_names(mock_config, conn_factory=mock_factory)

    assert tables == ["table1", "table2"]
    mock_cursor.execute.assert_called_once()

def test_get_all_table_names_failure(mock_config):
    mock_factory = MagicMock(side_effect=Exception("DB error"))
    result = get_all_table_names(mock_config, conn_factory=mock_factory)
    assert result == []

@patch("psycopg2.sql.SQL.as_string", return_value="SELECT * FROM public.table_name;")
@patch("pandas.read_sql_query")
def test_extract_table_data_success(mock_read_sql, mock_as_string, mock_config):
    mock_read_sql.return_value = pd.DataFrame({"a": [1], "b": [2]})

    mock_conn = MagicMock()
    mock_factory = MagicMock(return_value=MagicMock(__enter__=lambda x: mock_conn, __exit__=MagicMock()))

    result = extract_table_data("table_name", mock_config, conn_factory=mock_factory)
    assert isinstance(result, pd.DataFrame)
    mock_read_sql.assert_called_once()

@patch("pandas.read_sql_query", side_effect=Exception("read failed"))
def test_extract_table_data_failure(mock_read_sql, mock_config):
    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = False

    mock_factory = MagicMock(return_value=mock_conn)

    result = extract_table_data("bad_table", mock_config, conn_factory=mock_factory)

    assert isinstance(result, pd.DataFrame)
    assert result.empty

