##############################################
# File: cleanup_config_loader.py
# Description: Load config for cleanup DAG
# Author: Christopher Romanillos
# Date: 2025-06-28
##############################################

import yaml
from src.utils.pipeline import initialize_pipeline

def load_cleanup_config():
    with open("/opt/airflow/config/cleanup_config.yaml") as f:
        config = yaml.safe_load(f)

    logger = initialize_pipeline("postgres_cleanup")
    return config, logger

