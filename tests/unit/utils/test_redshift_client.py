import pytest
from unittest.mock import MagicMock, patch
from src.utils.redshift_client import get_redshift_connection

@patch("src.utils.redshift_client.logger")
def test_get_redshift_connection_success(mock_logger):
    """Test successful Redshift connection creation and info logging."""
    mock_connect = MagicMock()
    config = {"redshift": {"connection_string": "redshift://user:pass@host:5439/db"}}

    # Call the function with the mock connector function
    conn = get_redshift_connection(config, connector_fn=mock_connect)

    # Assert the mock connector was called with correct connection string
    mock_connect.assert_called_once_with("redshift://user:pass@host:5439/db")
    # Assert the returned connection is what the mock connector returns
    assert conn == mock_connect.return_value
    # Assert the logger.info was called once with expected message
    mock_logger.info.assert_called_once_with("🔗 Connecting to Redshift.")

@patch("src.utils.redshift_client.logger")
def test_get_redshift_connection_failure(mock_logger):
    """Test that connection failure raises and logs error."""
    def failing_connect(_):
        raise Exception("connection failed")

    config = {"redshift": {"connection_string": "redshift://user:pass@host:5439/db"}}

    # Expect an exception to be raised with matching message
    with pytest.raises(Exception, match="connection failed"):
        get_redshift_connection(config, connector_fn=failing_connect)

    # Assert the logger.error was called at least once
    mock_logger.error.assert_called()
