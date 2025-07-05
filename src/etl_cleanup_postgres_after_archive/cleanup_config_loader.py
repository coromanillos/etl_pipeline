###############################################
# File: cleanup_config_loader.py (Refactored)
# Description: Load config + logger for cleanup DAG
# Author: Christopher Romanillos
# Date: 2025-06-28
###############################################

from src.utils.config import load_config
from src.utils.pipeline import initialize_pipeline

def load_cleanup_config():
    config = load_config("/opt/airflow/config/cleanup_config.yaml")
    logger = initialize_pipeline("postgres_cleanup")
    return config, logger