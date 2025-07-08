# test_cleanup_config_loader
 
import pytest
from unittest.mock import patch, MagicMock
from src.cleanup.cleanup_config_loader import load_cleanup_config

@patch("src.cleanup.cleanup_config_loader.load_config")
@patch("src.cleanup.cleanup_config_loader.initialize_pipeline")
def test_load_cleanup_config_uses_env_path(mock_init_logger, mock_load_config):
    mock_load_config.return_value = {"key": "value"}
    mock_init_logger.return_value = MagicMock()

    config, logger = load_cleanup_config()

    assert config == {"key": "value"}
    assert logger is not None
