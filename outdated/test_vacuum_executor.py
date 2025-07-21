# test_vaccum_executor
import pytest
from unittest.mock import patch, MagicMock
from src.utils.postgres_cleaner import vacuum_postgres


@pytest.fixture
def config():
    return {"postgres_loader": {"connection_string": "postgresql://..."}}


@patch("src.utils.postgres_cleaner.get_postgres_connection")
def test_vacuum_postgres_success(mock_get_conn, config):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    vacuum_postgres(config)

    mock_cursor.execute.assert_called_once_with("VACUUM FULL;")
    mock_conn.commit.assert_called_once()


@patch("src.utils.postgres_cleaner.get_postgres_connection", side_effect=Exception("Vacuum failed"))
def test_vacuum_postgres_failure(mock_get_conn, config):
    with pytest.raises(Exception, match="Vacuum failed"):
        vacuum_postgres(config)
