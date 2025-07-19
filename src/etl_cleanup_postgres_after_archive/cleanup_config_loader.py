###############################################
# File: cleanup_config_loader.py (Refactored)
# Description: Load config + logger for cleanup DAG
# Author: Christopher Romanillos
# Date: 2025-06-28
###############################################

import os
from src.utils.config import load_config
from src.utils.pipeline import initialize_pipeline

def load_cleanup_config(config_path=None):
    # Defer config path resolution here to runtime only
    path = config_path or os.getenv("CLEANUP_CONFIG_PATH", "/opt/airflow/config/cleanup_config.yaml")
    config = load_config(path)
    logger = initialize_pipeline("postgres_cleanup")
    return config, logger
