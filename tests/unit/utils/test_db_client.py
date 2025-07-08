import pytest
from unittest.mock import MagicMock, patch
from src.utils.db_client import get_postgres_connection

def test_get_postgres_connection_success():
    """Test successful Postgres connection creation."""
    mock_connect = MagicMock()
    config = {"postgres_loader": {"connection_string": "postgresql://user:pass@localhost:5432/db"}}

    conn = get_postgres_connection(config, connector_fn=mock_connect)

    mock_connect.assert_called_once_with("postgresql://user:pass@localhost:5432/db")
    assert conn == mock_connect.return_value

@patch("src.utils.db_client.logger")
def test_get_postgres_connection_failure(mock_logger):
    """Test failure in Postgres connection raises and logs error."""
    def failing_connect(_):
        raise Exception("boom")

    config = {"postgres_loader": {"connection_string": "postgresql://user:pass@localhost:5432/db"}}

    with pytest.raises(Exception, match="boom"):
        get_postgres_connection(config, connector_fn=failing_connect)

    mock_logger.error.assert_called()
