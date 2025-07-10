#############################################################################
# Title: pipeline.py
# Author: Christopher Romanillos
# Description: Loads config and logger for a named pipeline component
# Date: 2025-05-18 | Version: 2.1
#############################################################################

import logging
import os

def initialize_pipeline(component_name: str):
    # Always get a standard logger for the component
    logger = logging.getLogger(component_name)

    # Optional: Set up basic config if needed (only once in main entry point)
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(level=logging.INFO)

    logger.info(f"[{component_name}] pipeline initialized.")
    return logger
