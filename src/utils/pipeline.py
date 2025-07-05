#############################################################################
# Title: pipeline.py
# Author: Christopher Romanillos
# Description: Loads config and logger for a named pipeline component
# Date: 2025-05-18 | Version: 2.1
#############################################################################

import logging
import os

def initialize_pipeline(component_name: str):
    """
    Initializes logging for a pipeline component, respecting Airflow context.

    Args:
        component_name (str): Logical name of the component.

    Returns:
        Logger: appropriate logger instance.
    """
    if "AIRFLOW_CTX_DAG_ID" in os.environ:
        logger = logging.getLogger(component_name)
    else:
        from utils.logging import get_logger
        logger = get_logger(module_name=component_name, force_setup=True)

    logger.info(f"[{component_name}] pipeline initialized.")
    return logger

