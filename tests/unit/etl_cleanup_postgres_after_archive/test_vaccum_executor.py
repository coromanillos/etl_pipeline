# test_vaccum_executor
import pytest
from unittest.mock import patch, MagicMock
from src.cleanup.vacuum_executor import vacuum_postgres

@pytest.fixture
def config():
    return {"postgres_loader": {"connection_string": "postgresql://..."}}  # Use actual test string in real case

@pytest.fixture
def logger():
    return MagicMock()

@patch("src.cleanup.vacuum_executor.get_postgres_connection")
def test_vacuum_postgres_success(mock_get_conn, config, logger):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    vacuum_postgres(config, logger)

    mock_cursor.execute.assert_called_once_with("VACUUM FULL;")
    mock_conn.commit.assert_called_once()
    logger.info.assert_called_once_with("✅ VACUUM FULL executed successfully.")

@patch("src.cleanup.vacuum_executor.get_postgres_connection", side_effect=Exception("Vacuum failed"))
def test_vacuum_postgres_failure(mock_get_conn, config, logger):
    with pytest.raises(Exception, match="Vacuum failed"):
        vacuum_postgres(config, logger)

    logger.error.assert_called()
