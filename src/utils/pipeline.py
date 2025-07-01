#############################################################################
# Title: pipeline.py
# Author: Christopher Romanillos
# Description: Loads config and logger for a named pipeline component
# Date: 2025-05-18 | Version: 2.1
#############################################################################

from utils.logging import get_logger, load_config

def initialize_pipeline(component_name: str, config_path: str = "/opt/airflow/config/config.yaml"):
    """
    Loads configuration and sets up a structured logger for the given component.

    Args:
        component_name (str): Logical name of the component (e.g. 'extract', 'transform', 'etl_dag').
        config_path (str): Path to config.yaml, defaulting to Airflow container location.

    Returns:
        tuple: (dict: config, Logger: structured logger)
    """
    config = load_config(config_path)
    logger = get_logger(module_name=component_name, config_path=config_path)
    logger.info(f"[{component_name}] pipeline initialized.")
    return config, logger
