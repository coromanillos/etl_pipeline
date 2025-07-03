##############################################
# File: cleanup_config_loader.py
# Description: Load config for cleanup DAG
# Author: Christopher Romanillos
# Date: 2025-06-28
##############################################

from src.utils.pipeline import initialize_pipeline

def load_cleanup_config():
    config, logger = initialize_pipeline(
        component_name="postgres_cleanup",
        config_path="/opt/airflow/config/config.yaml"
    )
    return config, logger
