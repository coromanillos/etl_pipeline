###############################################
# File: cleanup_config_loader.py (Refactored)
# Description: Load config for cleanup DAG
# Author: Christopher Romanillos
# Date: 2025-06-28
###############################################

import os
from src.utils.config import load_config


def load_cleanup_config(config_path: str = None) -> dict:
    # Defer config path resolution to runtime
    path = config_path or os.getenv("POSTGRES_CLEANUP_CONFIG_PATH", "/opt/airflow/config/cleanup_config.yaml")
    return load_config(path)
