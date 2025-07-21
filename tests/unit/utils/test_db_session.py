# tests/unit/test_db_session.py

import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import SQLAlchemyError
from src.utils.db_session import get_db_session

def test_get_db_session_success():
    mock_engine_factory = MagicMock()
    mock_session_factory = MagicMock()
    mock_session_instance = MagicMock()
    mock_session_factory.return_value = mock_session_instance

    config = {"postgres_loader": {"connection_string": "postgresql://user:pass@localhost/db"}}

    session_local = get_db_session(config, engine_factory=mock_engine_factory, session_factory=mock_session_factory)

    mock_engine_factory.assert_called_once_with(config["postgres_loader"]["connection_string"])
    mock_session_factory.assert_called_once()
    assert session_local == mock_session_instance

def test_get_db_session_no_config():
    with pytest.raises(ValueError, match="No config provided"):
        get_db_session(None)

def test_get_db_session_missing_connection_string():
    config = {"postgres_loader": {}}
    with pytest.raises(KeyError):
        get_db_session(config)

def test_get_db_session_sqlalchemy_error():
    def failing_engine_factory(url):
        raise SQLAlchemyError("engine failure")

    config = {"postgres_loader": {"connection_string": "postgresql://user:pass@localhost/db"}}

    with pytest.raises(SQLAlchemyError):
        get_db_session(config, engine_factory=failing_engine_factory)

def test_get_db_session_unexpected_exception():
    def bad_engine_factory(url):
        raise RuntimeError("unexpected error")

    config = {"postgres_loader": {"connection_string": "postgresql://user:pass@localhost/db"}}

    with pytest.raises(RuntimeError):
        get_db_session(config, engine_factory=bad_engine_factory)
