#############################################################################
# Title: pipeline.py
# Author: Christopher Romanillos
# Description: Loads config and logger for a named pipeline component
# Date: 2025-05-18 | Version: 2.1
#############################################################################

import logging
import os

def initialize_pipeline(component_name: str, logger_fn=None):
    logger_fn = logger_fn or get_logger

    if "AIRFLOW_CTX_DAG_ID" in os.environ:
        logger = logging.getLogger(component_name)
    else:
        logger = logger_fn(module_name=component_name, force_setup=True)

    logger.info(f"[{component_name}] pipeline initialized.")
    return logger
