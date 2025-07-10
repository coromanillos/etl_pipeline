import pytest
import os
from unittest.mock import MagicMock, patch
from src.utils.pipeline import initialize_pipeline

def test_initialize_pipeline_with_airflow_context(monkeypatch):
    monkeypatch.setenv("AIRFLOW_CTX_DAG_ID", "test_dag")

    with patch("src.utils.pipeline.logging.getLogger") as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        logger = initialize_pipeline("component_x")
        assert logger == mock_logger
        mock_logger.info.assert_called_with("[component_x] pipeline initialized.")

def test_initialize_pipeline_standalone():
    with patch("src.utils.pipeline.logging.getLogger") as mock_get_logger:
        fake_logger = MagicMock()
        mock_get_logger.return_value = fake_logger

        logger = initialize_pipeline("component_y")
        assert logger == fake_logger
        fake_logger.info.assert_called_with("[component_y] pipeline initialized.")
